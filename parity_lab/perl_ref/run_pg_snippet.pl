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
    };
    if ($@) {
        # Fallback to minimal environment if WeBWorK modules not available
        warn "WeBWorK::PG modules not found, using minimal environment\n";
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
    
    # Preprocess BEGIN_TEXT/END_TEXT blocks - simple string replacement
    # BEGIN_TEXT and END_TEXT are source filters, but we'll convert to TEXT() calls
    my $in_text = 0;
    my @lines = split(/\n/, $pg_content);
    my @new_lines = ();
    my $text_content = '';
    
    for my $line (@lines) {
        if ($line =~ /^BEGIN_TEXT/) {
            $in_text = 1;
            $text_content = '';
            next;
        } elsif ($line =~ /^END_TEXT/) {
            $in_text = 0;
            # Convert accumulated text to TEXT() call
            push @new_lines, "TEXT($text_content);";
            $text_content = '';
            next;
        }
        
        if ($in_text) {
            # Accumulate text content, handling variable interpolation
            $text_content .= ($text_content ? " . " : "") . qq{"$line\\n"};
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
        for my $ans_name (sort keys %{$main::PG->{PG_ANSWERS_HASH}}) {
            my $ans_group = $main::PG->{PG_ANSWERS_HASH}->{$ans_name};
            my $ans_eval = undef;
            my $ans_type = 'unknown';
            
            # Extract evaluator from PGanswergroup
            if (ref($ans_group) eq 'PGanswergroup') {
                $ans_eval = $ans_group->{ans_eval};
                $ans_type = ref($ans_eval) || 'unknown';
            } else {
                # Fallback: might be stored directly
                $ans_eval = $ans_group;
                $ans_type = ref($ans_eval) || 'unknown';
            }
            
            push @{$output->{answers}}, {
                name => $ans_name,
                correct => 0,
                score => 0,
                message => '',
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
    for my $ans_name (sort keys %PG_ANSWERS_HASH) {
        my $ans = $PG_ANSWERS_HASH{$ans_name};
        push @{$output->{answers}}, {
            name => $ans_name,
            correct => $ans->{correct} // 0,
            score => $ans->{score} // 0,
            message => $ans->{ans_message} // '',
            type => ref($ans->{evaluator}) // 'unknown',
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
