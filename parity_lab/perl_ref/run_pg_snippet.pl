#!/usr/bin/env perl
################################################################################
# Perl Runtime Adapter for Parity Testing
# Executes a PG snippet and serializes outputs to JSON for comparison with Python
################################################################################

use strict;
use warnings;
use v5.20;
use FindBin;
use lib "$FindBin::Bin/../../lib";
use lib "$FindBin::Bin/../..";  # For macros
use JSON;
use Carp;

# Load WeBWorK PG modules
BEGIN {
    eval {
        require WeBWorK::PG;
        require WeBWorK::PG::Translator;
        require WeBWorK::PG::Environment;
        $WeBWorK::PG::LOADED = 1;
    };
    if ($@) {
        # Fallback to minimal environment if WeBWorK modules not available
        warn "WeBWorK::PG modules not found, using minimal environment\n" if $@;
        $WeBWorK::PG::LOADED = 0;
    }
}

# Minimal PG environment setup
our $displayMode = 'HTML';
our $problemSeed;
our $envir = {};
our $PG_OUTPUT = '';
our %PG_ANSWERS_HASH = ();

sub usage {
    print STDERR "Usage: $0 <snippet.pg> <seed> <output.json>\n";
    exit 1;
}

# Parse command line
usage() unless @ARGV == 3;
my ($snippet_file, $seed, $output_json) = @ARGV;

# Convert to absolute path if relative
unless ($snippet_file =~ /^\//) {
    if (-f "$FindBin::Bin/../$snippet_file") {
        $snippet_file = "$FindBin::Bin/../$snippet_file";
    } elsif (-f "$FindBin::Bin/../../$snippet_file") {
        $snippet_file = "$FindBin::Bin/../../$snippet_file";
    } elsif (-f $snippet_file) {
        # Already correct relative path
    } else {
        die "Snippet file not found: $snippet_file\n";
    }
}

die "Snippet file not found: $snippet_file\n" unless -f $snippet_file;
$problemSeed = $seed;

# Setup environment with all required fields for PGcore
$envir = {
    DOCUMENT_ROOT => "$FindBin::Bin/../..",
    displayMode => $displayMode,
    problemSeed => $problemSeed,
    inputs_ref => {
        submittedAnswers => 0,
    },
    psvn => 12345,
    probNum => 1,
    templateDirectory => "$FindBin::Bin/../../",
    macrosPath => [
        "$FindBin::Bin/../../macros/core",
        "$FindBin::Bin/../../macros/parsers",
        "$FindBin::Bin/../../macros/contexts",
        "$FindBin::Bin/../../macros/ui",
        "$FindBin::Bin/../../macros/math",
        "$FindBin::Bin/../../macros/graph",
        "$FindBin::Bin/../../macros/answers",
        "$FindBin::Bin/../../macros",
    ],
    probFileName => $snippet_file,
    pwd => "$FindBin::Bin/../../",
    htmlDirectory => "$FindBin::Bin/../../",
    htmlURL => "/",
    tempDirectory => "/tmp",
    tempURL => "/tmp",
    problemUUID => "test-uuid",
    language_subroutine => sub { shift; return shift; },  # Simple maketext function
};

# Setup minimal WeBWorK::PG::IO environment if needed
BEGIN {
    unless (defined $WeBWorK::PG::IO::pg_envir) {
        $WeBWorK::PG::IO::pg_envir = {
            directories => {
                html_temp => "/tmp",
            },
        };
    }
}

# Prepare output structure
my $output = {
    tex => '',
    html => '',
    answers => [],
    errors => [],
    warnings => [],
};

# Capture warnings
my @warnings;
local $SIG{__WARN__} = sub {
    my $msg = shift;
    push @warnings, $msg;
    push @{$output->{warnings}}, $msg;
};

    # Eval the PG snippet in a controlled environment
    eval {
        # Clear output buffer
        $PG_OUTPUT = '';
        %PG_ANSWERS_HASH = ();

        # Load the PG file content
        open my $fh, '<', $snippet_file or die "Cannot open $snippet_file: $!";
        my $pg_content = do { local $/; <$fh> };
        close $fh;

        # Create a minimal PG execution environment
        # This is a simplified version - full PG needs WeBWorK::PG::Translator

        # Process the PG file in main package
        package main;
        
        # Declare global variables that PG code expects
        our ($displayMode, $problemSeed, $envir, $PG_OUTPUT, %PG_ANSWERS_HASH);
        
        # Initialize variables
        $main::displayMode = $displayMode;
        $main::problemSeed = $problemSeed;
        
        # DOCUMENT() expects %envir to be a hash, not a hash reference
        # So we need to populate %main::envir as a hash
        %main::envir = %$envir;
        
        # Initialize variables that macros expect
        $main::problemPreamble = {} unless defined $main::problemPreamble;
        $main::inputs_ref = $envir->{inputs_ref} unless defined $main::inputs_ref;
        
        # Load required modules in correct order
        # Add lib directory to @INC
        use lib "$FindBin::Bin/../../lib";
        
        # Load WeBWorK::PG::IO first (needed by PGcore)
        eval {
            require WeBWorK::PG::IO;
        };
        
        # Load WeBWorK::PG::Translator to get PG_restricted_eval
        eval {
            require WeBWorK::PG::Translator;
        };
        
        # Define PG_restricted_eval and PG_macro_file_eval in main package (needed by PG.pl)
        *main::PG_restricted_eval = sub {
            my @input = @_;
            return WeBWorK::PG::Translator::PG_restricted_eval(@input);
        };
        
        *main::PG_macro_file_eval = sub {
            my @input = @_;
            return WeBWorK::PG::Translator::PG_macro_file_eval(@input);
        };
        
        # Pre-load commonly used classes that macros depend on
        # These are loaded on-demand by macros, but we'll pre-load them to avoid errors
        eval {
            require ChoiceList;
            require Multiple;
            require Match;
            require Select;
        };
        # Ignore errors - they'll be loaded when needed by macros
        
        # Load Parser and MathObjects (needed for answer checking)
        eval {
            require Parser;
            require Parser::Context;
            require Value::Context;
            # Load default contexts (needed for getCopy to work)
            require Parser::Context::Default;
            # Load Legacy contexts (needed for num_cmp)
            require Parser::Legacy::Numeric;
            # Initialize parser context
            $main::_parser_loaded = 1;
            # Initialize context hash (PG.pl expects %main::context to be a hash)
            %main::context = ();
            # Set current context - this will create/bless the context properly
            Parser::Context->current(\%main::context);
        };
        if ($@) {
            warn "Warning: Could not load Parser: $@";
            # Fallback: create empty context hash
            %main::context = () unless defined $main::context;
        }

        # CRITICAL FIX: Load contextExtensions.pl and wrap context::Extensions::create
        # This fixes the "Can't call method \"operators\" on unblessed reference" error
        # in contextFraction.pl when extending() calls create() which calls getCopy()
        eval {
            # Load contextExtensions.pl macro file to define context::Extensions
            my $contextExtPath = "$FindBin::Bin/../../macros/contexts/contextExtensions.pl";
            if (-f $contextExtPath) {
                no strict 'vars';
                no warnings 'redefine';
                do $contextExtPath;
                if ($@) {
                    warn "Warning: Error loading contextExtensions.pl: $@\n";
                } else {
                    # Install wrapper around context::Extensions::create
                    if (defined(&context::Extensions::create)) {
                        my $original_create = \&context::Extensions::create;
                        *context::Extensions::create = sub {
                            my ($new, $from) = @_;
                            # Instead of calling the original, reimplement it with proper context table passing
                            # This ensures getCopy can find contexts in %main::context
                            my $name = "$new-$from";
                            my $context;
                            if (Value::isContext($from)) {
                                $context = $from->copy;
                            } else {
                                # THE FIX: Pass \%main::context as the context table to getCopy
                                # Ensure the base context exists in the table first
                                if (!defined($main::context{$from})) {
                                    # Try to get it from Default context with context table
                                    my $base = Parser::Context->getCopy(\%main::context, $from);
                                    if (!$base) {
                                        # If still not found, try without context table
                                        $base = Parser::Context->getCopy($from);
                                    }
                                    if (!$base && $from =~ /^Limited/) {
                                        # If it's a Limited context and not found, create from Numeric
                                        my $numeric = Parser::Context->getCopy(\%main::context, "Numeric");
                                        if ($numeric) {
                                            $base = $numeric->copy;
                                            $base->{name} = $from;
                                            # Add Limited-specific settings
                                            $base->operators->undefine('+', '-', '*', '/', '**', '^', 'U', ' ');
                                            $base->functions->disable('All');
                                        }
                                    }
                                    $main::context{$from} = $base if $base;
                                }
                                $context = Parser::Context->getCopy(\%main::context, $from);
                            }
                            # Set the context properties
                            if ($context) {
                                $context->{baseName}  = $new;
                                $context->{name}      = $name;
                                $main::context{$name} = $context;
                            }
                            return $context;
                        };
                    }
                }
            }
        };

        # Try to load HTML::Entities if available (needed by PGcore)
        eval {
            require HTML::Entities;
        };
        # If not available, define a minimal version
        unless (defined(&HTML::Entities::encode_entities)) {
            no strict 'refs';
            *{'HTML::Entities::encode_entities'} = sub {
                my ($text) = @_;
                $text =~ s/&/&amp;/g;
                $text =~ s/</&lt;/g;
                $text =~ s/>/&gt;/g;
                $text =~ s/"/&quot;/g;
                return $text;
            };
        }
        
        # Load PGcore first (required by PG.pl)
        eval {
            require PGcore;
        };
        if ($@) {
            warn "Warning: Could not load PGcore: $@";
        }
        
        # Load PG.pl to set up functions like DOCUMENT, TEXT, etc.
        my $pg_pl_path = "$FindBin::Bin/../../macros/PG.pl";
        if (-f $pg_pl_path) {
            no strict 'vars';
            no strict 'refs';
            no strict 'subs';
            local $@;
            do $pg_pl_path;
            if ($@) {
                warn "Warning: Error loading PG.pl: $@";
            }
            # Call _PG_init if it exists to initialize the context properly
            if (defined(&main::_PG_init)) {
                main::_PG_init();
            }
            # Ensure context is properly initialized as a context table
            # The context table needs to have a {current} key pointing to a blessed context object
            unless (defined($main::context{current}) && ref($main::context{current}) =~ /^Parser::Context/) {
                Parser::Context->current(\%main::context);
            }

            # Ensure base contexts are initialized (needed for context extensions like Fraction)
            # These contexts are needed by context::Extensions::create()
            # getCopy will now ensure they are properly blessed via our wrapper
            eval {
                # Ensure Numeric context is available in %main::context
                unless (defined($main::context{Numeric})) {
                    my $numeric = Parser::Context->getCopy(\%main::context, "Numeric");
                    $main::context{Numeric} = $numeric if $numeric;
                }
                # Ensure LimitedNumeric context is available
                unless (defined($main::context{LimitedNumeric})) {
                    my $limited = Parser::Context->getCopy(\%main::context, "LimitedNumeric");
                    $main::context{LimitedNumeric} = $limited if $limited;
                }
            };
            
            # Fix any contexts in %main::context that aren't properly blessed
            # This is needed because Init() functions may create contexts that aren't blessed
            eval {
                for my $key (keys %main::context) {
                    my $ctx = $main::context{$key};
                    if ($ctx && ref($ctx) && ref($ctx) !~ /^Parser::Context/) {
                        if (ref($ctx) eq 'HASH') {
                            bless($ctx, "Parser::Context");
                        }
                    }
                }
            };
        }

        # Don't define minimal functions - let PG.pl handle them
        # But we need to capture TEXT output, so override it after PG.pl loads
        # We'll do this after DOCUMENT() is called

    # loadMacros will be defined by PG.pl, but we need to override it
    # to capture output. Actually, let PG.pl handle it and just capture TEXT

    # Override ANS and NAMED_ANS to capture answers
    # These will be overridden by PG.pl, so we need to override after PG.pl loads
    # But we'll define them here as a fallback

    # Execute the PG snippet in main package with proper scoping
    # PG code expects variables to be in main:: package
    package main;
    
    # Make sure envir is accessible and macrosPath is set
    # DOCUMENT() uses \%envir, so %main::envir must be a hash
    # Ensure macrosPath is always an array ref
    $main::envir{macrosPath} = $envir->{macrosPath} || [];
    
    # Disable strict - PG code uses global variables and barewords
    no strict 'vars';
    no strict 'refs';
    no strict 'subs';  # Allow barewords like PGstandard
    no warnings 'redefine';
    no warnings 'once';
    
    # Override TEXT to capture output (after PG.pl loads)
    # But only if TEXT is defined
    if (defined(&main::TEXT)) {
        my $original_TEXT = \&main::TEXT;
        *main::TEXT = sub {
            $main::PG_OUTPUT .= join('', @_);
            # Also call original
            $original_TEXT->(@_);
        };
    } else {
        # Define TEXT if it doesn't exist
        *main::TEXT = sub {
            $main::PG_OUTPUT .= join('', @_);
        };
    }
    
    # Override ANS and NAMED_ANS to capture answers (after PG.pl loads)
    if (defined(&main::ANS)) {
        my $original_ANS = \&main::ANS;
        *main::ANS = sub {
            my ($evaluator) = @_;
            # Call original ANS to register with PG
            $original_ANS->(@_);
            # Also capture in our hash
            my $ans_name = "AnSwEr" . (scalar(keys %main::PG_ANSWERS_HASH) + 1);
            $main::PG_ANSWERS_HASH{$ans_name} = {
                evaluator => $evaluator,
                correct => 0,
                score => 0,
                ans_message => '',
            };
        };
    }
    
    if (defined(&main::NAMED_ANS)) {
        my $original_NAMED_ANS = \&main::NAMED_ANS;
        *main::NAMED_ANS = sub {
            my ($name, $evaluator) = @_;
            # Call original NAMED_ANS to register with PG
            $original_NAMED_ANS->(@_);
            # Also capture in our hash
            $main::PG_ANSWERS_HASH{$name} = {
                evaluator => $evaluator,
                correct => 0,
                score => 0,
                ans_message => '',
            };
        };
    }
    
    # Preprocess BEGIN_TEXT/END_TEXT, BEGIN_PGML/END_PGML, BEGIN_SOLUTION/END_SOLUTION, BEGIN_HINT/END_HINT
    # These are source filters, but we'll convert them to function calls
    my $in_text = 0;
    my $in_pgml = 0;
    my $in_solution = 0;
    my $in_hint = 0;
    my @lines = split(/\n/, $pg_content);
    my @new_lines = ();
    my $text_content = '';
    my $pgml_content = '';
    my $solution_content = '';
    my $hint_content = '';
    
    for my $line (@lines) {
        # Handle BEGIN_TEXT/END_TEXT
        if ($line =~ /^BEGIN_TEXT/) {
            $in_text = 1;
            $text_content = '';
            next;
        } elsif ($line =~ /^END_TEXT/) {
            $in_text = 0;
            # Convert accumulated text to TEXT() call
            # Use heredoc syntax to avoid issues with quotes and braces
            my $heredoc_id = "TEXT_BLOCK_" . int(rand(1000000));
            push @new_lines, "my \$$heredoc_id = <<'EOTEXT';";
            push @new_lines, $text_content;
            push @new_lines, "EOTEXT";
            push @new_lines, "TEXT(\$$heredoc_id);";
            $text_content = '';
            next;
        }
        
        # Handle BEGIN_PGML/END_PGML
        # BEGIN_PGML/END_PGML are source filters that convert PGML to TEXT() calls
        # We'll convert them to PGML() function calls
        if ($line =~ /^BEGIN_PGML/) {
            $in_pgml = 1;
            $pgml_content = '';
            next;
        } elsif ($line =~ /^END_PGML/) {
            $in_pgml = 0;
            # Convert PGML content to PGML() function call
            # PGML() is defined by PGML.pl and processes the content
            my $pgml_quoted = '';
            for my $pgml_line (split(/\n/, $pgml_content)) {
                $pgml_line =~ s/"/\\"/g;  # Escape quotes
                $pgml_quoted .= ($pgml_quoted ? "\\n" : "") . $pgml_line;
            }
            push @new_lines, "TEXT(PGML(qq{$pgml_quoted}));";
            $pgml_content = '';
            next;
        }
        
        # Handle BEGIN_SOLUTION/END_SOLUTION
        if ($line =~ /^BEGIN_SOLUTION/) {
            $in_solution = 1;
            $solution_content = '';
            next;
        } elsif ($line =~ /^END_SOLUTION/) {
            $in_solution = 0;
            # Convert solution content to SOLUTION() call
            my $heredoc_id = "SOLUTION_BLOCK_" . int(rand(1000000));
            push @new_lines, "my \$$heredoc_id = <<'EOSOLUTION';";
            push @new_lines, $solution_content;
            push @new_lines, "EOSOLUTION";
            push @new_lines, "SOLUTION(\$$heredoc_id);";
            $solution_content = '';
            next;
        }
        
        # Handle BEGIN_HINT/END_HINT
        if ($line =~ /^BEGIN_HINT/) {
            $in_hint = 1;
            $hint_content = '';
            next;
        } elsif ($line =~ /^END_HINT/) {
            $in_hint = 0;
            # Convert hint content to HINT() call
            my $heredoc_id = "HINT_BLOCK_" . int(rand(1000000));
            push @new_lines, "my \$$heredoc_id = <<'EOHINT';";
            push @new_lines, $hint_content;
            push @new_lines, "EOHINT";
            push @new_lines, "HINT(\$$heredoc_id);";
            $hint_content = '';
            next;
        }
        
        if ($in_text) {
            # Accumulate text content - preserve the line as-is for variable interpolation
            $text_content .= ($text_content ? "\n" : "") . $line;
        } elsif ($in_pgml) {
            # Accumulate PGML content
            $pgml_content .= ($pgml_content ? "\n" : "") . $line;
        } elsif ($in_solution) {
            # Accumulate solution content
            $solution_content .= ($solution_content ? "\n" : "") . $line;
        } elsif ($in_hint) {
            # Accumulate hint content
            $hint_content .= ($hint_content ? "\n" : "") . $line;
        } else {
            push @new_lines, $line;
        }
    }
    
    $pg_content = join("\n", @new_lines);
    
    eval $pg_content;
    if ($@) {
        die "Error executing PG snippet: $@\n";
    }
};

if ($@) {
    push @{$output->{errors}}, "$@";
}

# Collect outputs
# Try to get output from $PG object if it exists, otherwise use our buffer
if (defined($main::PG) && ref($main::PG) eq 'PGcore') {
    # Get output from PG object's OUTPUT_ARRAY
    my @output_array = @{$main::PG->{OUTPUT_ARRAY} || []};
    $output->{html} = join('', @output_array);
    $output->{tex} = join('', @output_array);
    
    # Also collect answers from PG object
    # Answers are stored as PGanswergroup objects in PG_ANSWERS_HASH
    if (defined($main::PG->{PG_ANSWERS_HASH})) {
        # First, get correct answers by using WeBWorK::PG with processAnswers => 1
        # Even with empty inputs, WeBWorK::PG populates correct_ans
        my $correct_answers = {};
        if ($WeBWorK::PG::LOADED) {
            eval {
                # Set PG_ROOT if not already set
                local $ENV{PG_ROOT} = $ENV{PG_ROOT} || "$FindBin::Bin/../..";
                
                # Use the snippet_file as-is (should be absolute path now)
                my $pg_correct = WeBWorK::PG->new(
                    sourceFilePath => $snippet_file,
                    problemSeed => $seed,
                    processAnswers => 1,
                    inputs_ref => {},
                );
                
                # Extract correct answers from the answers hash
                for my $ans_name (keys %{$pg_correct->{answers}}) {
                    my $ans = $pg_correct->{answers}{$ans_name};
                    my $correct_ans = $ans->{correct_ans} || '';
                    $correct_answers->{$ans_name} = $correct_ans;
                    
                    # Also map to AnSwEr1 format (without leading zeros)
                    if ($ans_name =~ /^AnSwEr0*(\d+)$/) {
                        my $num = $1;
                        $correct_answers->{"AnSwEr$num"} = $correct_ans;
                    }
                }
                
                # Debug output
                if (scalar(keys %$correct_answers) > 0) {
                    print STDERR "DEBUG: Got " . scalar(keys %$correct_answers) . " correct answers from WeBWorK::PG: " . join(", ", map { "$_=$correct_answers->{$_}" } sort keys %$correct_answers) . "\n" if $ENV{DEBUG};
                }
            };
            if ($@) {
                # If WeBWorK::PG fails, log the error for debugging
                print STDERR "DEBUG: WeBWorK::PG error: $@\n" if $ENV{DEBUG};
            }
        } else {
            print STDERR "DEBUG: WeBWorK::PG not loaded\n" if $ENV{DEBUG};
        }
        
        # Debug: show what we're iterating over
        if ($ENV{DEBUG}) {
            my @pg_keys = sort keys %{$main::PG->{PG_ANSWERS_HASH}};
            print STDERR "DEBUG: PG_ANSWERS_HASH has " . scalar(@pg_keys) . " keys: " . join(", ", @pg_keys) . "\n";
            print STDERR "DEBUG: correct_answers has " . scalar(keys %$correct_answers) . " keys: " . join(", ", sort keys %$correct_answers) . "\n";
        }
        
        for my $ans_name (sort keys %{$main::PG->{PG_ANSWERS_HASH}}) {
            print STDERR "DEBUG: Processing answer: $ans_name\n" if $ENV{DEBUG};
            my $ans_group = $main::PG->{PG_ANSWERS_HASH}->{$ans_name};
            my $ans_eval = undef;
            my $ans_type = 'unknown';
            my $correct_value = undef;
            my $score = 0;
            my $is_correct = 0;
            my $message = '';
            
            # Extract evaluator from PGanswergroup
            if (ref($ans_group) eq 'PGanswergroup') {
                $ans_eval = $ans_group->{ans_eval};
                $ans_type = ref($ans_eval) || 'unknown';
            } else {
                # Fallback: might be stored directly
                $ans_eval = $ans_group;
                $ans_type = ref($ans_eval) || 'unknown';
            }
            
            # Get correct answer - try correct_answers hash first (check both name formats)
            my $found_value = undef;
            
            # First try exact match
            if (exists($correct_answers->{$ans_name}) && $correct_answers->{$ans_name} ne '') {
                $found_value = $correct_answers->{$ans_name};
                print STDERR "DEBUG: Found exact match for $ans_name: $found_value\n" if $ENV{DEBUG};
            } else {
                # Try alternative name format - convert AnSwEr1 to AnSwEr0001
                my $alt_name = undef;
                if ($ans_name =~ /^AnSwEr(\d+)$/) {
                    $alt_name = "AnSwEr" . sprintf("%04d", $1);
                } elsif ($ans_name =~ /^AnSwEr0+(\d+)$/) {
                    $alt_name = "AnSwEr$1";
                }
                
                if (defined($alt_name) && $alt_name ne $ans_name) {
                    print STDERR "DEBUG: Trying alt_name $alt_name for $ans_name\n" if $ENV{DEBUG};
                    if (exists($correct_answers->{$alt_name}) && $correct_answers->{$alt_name} ne '') {
                        $found_value = $correct_answers->{$alt_name};
                        print STDERR "DEBUG: Found alt match: $found_value\n" if $ENV{DEBUG};
                    } else {
                        print STDERR "DEBUG: Alt name $alt_name not in hash\n" if $ENV{DEBUG};
                    }
                }
            }
            
            if (defined($found_value)) {
                $correct_value = $found_value;
                print STDERR "DEBUG: Set correct_value to $correct_value\n" if $ENV{DEBUG};
            } elsif (defined($ans_eval)) {
                # Try to get from evaluator
                if (ref($ans_eval) && $ans_eval->can('correct_ans')) {
                    $correct_value = $ans_eval->correct_ans;
                } elsif (ref($ans_eval) && exists($ans_eval->{correct_ans})) {
                    $correct_value = $ans_eval->{correct_ans};
                } elsif (ref($ans_eval) && $ans_eval->can('ans')) {
                    $correct_value = $ans_eval->ans;
                }
            }
            
            # Debug: check what we have
            print STDERR "DEBUG: Answer $ans_name: " if $ENV{DEBUG};
            print STDERR "correct_value=" . (defined($correct_value) ? $correct_value : "UNDEF") . ", " if $ENV{DEBUG};
            print STDERR "in hash=" . (exists($correct_answers->{$ans_name}) ? "YES($correct_answers->{$ans_name})" : "NO") . ", " if $ENV{DEBUG};
            if ($ENV{DEBUG}) {
                my $alt_name = $ans_name;
                if ($ans_name =~ /^AnSwEr(\d+)$/) {
                    $alt_name = "AnSwEr" . sprintf("%04d", $1);
                } elsif ($ans_name =~ /^AnSwEr0+(\d+)$/) {
                    $alt_name = "AnSwEr$1";
                }
                print STDERR "alt_name=$alt_name, alt_in_hash=" . (exists($correct_answers->{$alt_name}) ? "YES($correct_answers->{$alt_name})" : "NO") . ", ";
                print STDERR "hash keys=" . join(",", keys %$correct_answers) . "\n";
            }
            
            # Evaluate the correct answer - try direct evaluator first, then WeBWorK::PG
            if (defined($correct_value) && $correct_value ne '' && defined($ans_eval)) {
                print STDERR "DEBUG: Evaluating $ans_name with correct_value=$correct_value\n" if $ENV{DEBUG};
                
                eval {
                    # Try direct evaluation using the evaluator
                    if (ref($ans_eval) && $ans_eval->can('evaluate')) {
                        print STDERR "DEBUG: Trying direct evaluate() method\n" if $ENV{DEBUG};
                        my $result = $ans_eval->evaluate("$correct_value");
                        if (ref($result) && exists($result->{score})) {
                            $score = $result->{score};
                            $is_correct = ($score >= 1) ? 1 : 0;
                            $message = $result->{ans_message} || '';
                            print STDERR "DEBUG: Direct evaluation: score=$score\n" if $ENV{DEBUG};
                        } else {
                            print STDERR "DEBUG: Direct evaluation returned invalid result\n" if $ENV{DEBUG};
                        }
                    } else {
                        print STDERR "DEBUG: Evaluator doesn't have evaluate() method\n" if $ENV{DEBUG};
                    }
                };
                if ($@ && $ENV{DEBUG}) {
                    print STDERR "DEBUG: Direct evaluation error: $@\n";
                }
                
                # If direct evaluation didn't work, try WeBWorK::PG
                if ($score == 0 && $correct_value ne '' && $WeBWorK::PG::LOADED) {
                    print STDERR "DEBUG: Trying WeBWorK::PG fallback\n" if $ENV{DEBUG};
                    eval {
                        # Set PG_ROOT if not already set
                        local $ENV{PG_ROOT} = $ENV{PG_ROOT} || "$FindBin::Bin/../..";
                        
                        # Try both answer name formats (AnSwEr1 and AnSwEr0001)
                        my $inputs = {};
                        $inputs->{$ans_name} = $correct_value;
                        
                        # Also try with alternative format
                        if ($ans_name =~ /^AnSwEr(\d+)$/) {
                            my $num = $1;
                            $inputs->{"AnSwEr" . sprintf("%04d", $num)} = $correct_value;
                        } elsif ($ans_name =~ /^AnSwEr0+(\d+)$/) {
                            my $num = $1;
                            $inputs->{"AnSwEr$num"} = $correct_value;
                        }
                        
                        my $pg_check = WeBWorK::PG->new(
                            sourceFilePath => $snippet_file,
                            problemSeed => $seed,
                            processAnswers => 1,
                            inputs_ref => $inputs,
                        );
                        
                        # Check both name formats
                        my $ans_result = undef;
                        if (exists($pg_check->{answers}{$ans_name})) {
                            $ans_result = $pg_check->{answers}{$ans_name};
                        } else {
                            # Try alternative format
                            my $alt_name = $ans_name;
                            if ($ans_name =~ /^AnSwEr(\d+)$/) {
                                $alt_name = "AnSwEr" . sprintf("%04d", $1);
                            } elsif ($ans_name =~ /^AnSwEr0+(\d+)$/) {
                                $alt_name = "AnSwEr$1";
                            }
                            if ($alt_name ne $ans_name && exists($pg_check->{answers}{$alt_name})) {
                                $ans_result = $pg_check->{answers}{$alt_name};
                            }
                        }
                        
                        if (defined($ans_result)) {
                            $score = $ans_result->{score} || 0;
                            $is_correct = ($score >= 1) ? 1 : 0;
                            $message = $ans_result->{ans_message} || '';
                        }
                    };
                }
            }
            
            push @{$output->{answers}}, {
                name => $ans_name,
                correct => $is_correct,
                score => $score,
                message => $message,
                correct_value => defined($correct_value) ? "$correct_value" : undef,
                type => $ans_type,
            };
        }
    }
} else {
    $output->{html} = $PG_OUTPUT;
    $output->{tex} = $PG_OUTPUT;
}

# Process answers (only if not already collected from PG object)
if (scalar(@{$output->{answers}}) == 0) {
    # Get correct answers first
    my $correct_answers = {};
    if ($WeBWorK::PG::LOADED) {
        eval {
            local $ENV{PG_ROOT} = $ENV{PG_ROOT} || "$FindBin::Bin/../..";
            my $pg_correct = WeBWorK::PG->new(
                sourceFilePath => $snippet_file,
                problemSeed => $seed,
                processAnswers => 1,
                inputs_ref => {},
            );
            
            for my $ans_name (keys %{$pg_correct->{answers}}) {
                my $ans = $pg_correct->{answers}{$ans_name};
                my $correct_ans = $ans->{correct_ans} || '';
                $correct_answers->{$ans_name} = $correct_ans;
                if ($ans_name =~ /^AnSwEr0*(\d+)$/) {
                    my $num = $1;
                    $correct_answers->{"AnSwEr$num"} = $correct_ans;
                }
            }
        };
    }
    
    for my $ans_name (sort keys %PG_ANSWERS_HASH) {
        my $ans = $PG_ANSWERS_HASH{$ans_name};
        my $ans_eval = $ans->{evaluator};
        my $correct_value = undef;
        my $score = 0;
        my $is_correct = 0;
        my $message = '';
        
        # Get correct answer
        if (exists($correct_answers->{$ans_name}) && $correct_answers->{$ans_name} ne '') {
            $correct_value = $correct_answers->{$ans_name};
        } else {
            my $alt_name = undef;
            if ($ans_name =~ /^AnSwEr(\d+)$/) {
                $alt_name = "AnSwEr" . sprintf("%04d", $1);
            } elsif ($ans_name =~ /^AnSwEr0+(\d+)$/) {
                $alt_name = "AnSwEr$1";
            }
            if (defined($alt_name) && exists($correct_answers->{$alt_name}) && $correct_answers->{$alt_name} ne '') {
                $correct_value = $correct_answers->{$alt_name};
            }
        }
        
        # Evaluate the correct answer
        if (defined($correct_value) && $correct_value ne '' && defined($ans_eval)) {
            eval {
                if (ref($ans_eval) && $ans_eval->can('evaluate')) {
                    my $result = $ans_eval->evaluate("$correct_value");
                    if (ref($result) && exists($result->{score})) {
                        $score = $result->{score};
                        $is_correct = ($score >= 1) ? 1 : 0;
                        $message = $result->{ans_message} || '';
                    }
                }
            };
            
            # Fallback to WeBWorK::PG if direct evaluation didn't work
            if ($score == 0 && $WeBWorK::PG::LOADED) {
                eval {
                    local $ENV{PG_ROOT} = $ENV{PG_ROOT} || "$FindBin::Bin/../..";
                    my $inputs = {};
                    $inputs->{$ans_name} = $correct_value;
                    if ($ans_name =~ /^AnSwEr(\d+)$/) {
                        $inputs->{"AnSwEr" . sprintf("%04d", $1)} = $correct_value;
                    }
                    
                    my $pg_check = WeBWorK::PG->new(
                        sourceFilePath => $snippet_file,
                        problemSeed => $seed,
                        processAnswers => 1,
                        inputs_ref => $inputs,
                    );
                    
                    my $ans_result = undef;
                    if (exists($pg_check->{answers}{$ans_name})) {
                        $ans_result = $pg_check->{answers}{$ans_name};
                    } else {
                        my $alt_name = $ans_name =~ /^AnSwEr(\d+)$/ ? "AnSwEr" . sprintf("%04d", $1) : undef;
                        if (defined($alt_name) && exists($pg_check->{answers}{$alt_name})) {
                            $ans_result = $pg_check->{answers}{$alt_name};
                        }
                    }
                    
                    if (defined($ans_result)) {
                        $score = $ans_result->{score} || 0;
                        $is_correct = ($score >= 1) ? 1 : 0;
                        $message = $ans_result->{ans_message} || '';
                    }
                };
            }
        }
        
        push @{$output->{answers}}, {
            name => $ans_name,
            correct => $is_correct,
            score => $score,
            message => $message,
            correct_value => defined($correct_value) ? "$correct_value" : undef,
            type => ref($ans_eval) || 'unknown',
        };
    }
}

# Write JSON output
my $json = JSON->new->pretty->canonical;
open my $out_fh, '>', $output_json or die "Cannot write to $output_json: $!";
print $out_fh $json->encode($output);
close $out_fh;

print STDERR "✓ Perl output written: $output_json\n";
print STDERR "  Seed: $seed\n";
print STDERR "  HTML length: " . length($output->{html}) . " chars\n";
print STDERR "  Answers: " . scalar(@{$output->{answers}}) . "\n";
print STDERR "  Errors: " . scalar(@{$output->{errors}}) . "\n";

exit 0;
