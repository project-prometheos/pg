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
use JSON;
use Carp;

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

# Setup environment
$envir = {
    DOCUMENT_ROOT => "$FindBin::Bin/../..",
    displayMode => $displayMode,
    problemSeed => $problemSeed,
    inputs_ref => {},
    psvn => 12345,
    probNum => 1,
};

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

    # Process the PG file
    package main;
    our ($displayMode, $problemSeed, $envir, $PG_OUTPUT, %PG_ANSWERS_HASH);

    # Define minimal PG functions
    sub TEXT {
        $main::PG_OUTPUT .= join('', @_);
    }

    sub DOCUMENT {
        # Initialize problem
        return '';
    }

    sub ENDDOCUMENT {
        # Finalize problem
        return $main::PG_OUTPUT;
    }

    sub BEGIN_TEXT {
        # This is typically a heredoc delimiter, handled by source filter
        # For snippet testing, we'll capture in TEXT
    }

    sub loadMacros {
        my @files = @_;
        for my $file (@files) {
            my $macro_path;
            # Try different locations
            for my $dir ("$FindBin::Bin/../../macros/core",
                        "$FindBin::Bin/../../macros",
                        "$FindBin::Bin/../../macros/parsers",
                        "$FindBin::Bin/../../macros/contexts") {
                if (-f "$dir/$file") {
                    $macro_path = "$dir/$file";
                    last;
                }
            }
            if ($macro_path && -f $macro_path) {
                # Load the macro file
                do $macro_path or warn "Error loading $file: $@";
            } else {
                warn "Macro file not found: $file";
            }
        }
    }

    sub ANS {
        my ($evaluator) = @_;
        my $ans_name = "AnSwEr" . (scalar(keys %main::PG_ANSWERS_HASH) + 1);
        $main::PG_ANSWERS_HASH{$ans_name} = {
            evaluator => $evaluator,
            correct => 0,
            score => 0,
            ans_message => '',
        };
    }

    sub NAMED_ANS {
        my ($name, $evaluator) = @_;
        $main::PG_ANSWERS_HASH{$name} = {
            evaluator => $evaluator,
            correct => 0,
            score => 0,
            ans_message => '',
        };
    }

    # Execute the PG snippet
    eval $pg_content;
    if ($@) {
        die "Error executing PG snippet: $@\n";
    }
};

if ($@) {
    push @{$output->{errors}}, "$@";
}

# Collect outputs
$output->{html} = $PG_OUTPUT;
$output->{tex} = $PG_OUTPUT;  # In reality, would be different for TeX mode

# Process answers
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
