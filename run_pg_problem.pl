#!/usr/bin/env perl

use strict;
use warnings;

# Set PG_ROOT if not already set
unless ($ENV{PG_ROOT}) {
    use FindBin;
    $ENV{PG_ROOT} = $FindBin::Bin;
}

# Add local::lib path if it exists
if (-d "$ENV{HOME}/perl5/lib/perl5") {
    use lib "$ENV{HOME}/perl5/lib/perl5";
}

# Add lib directory to @INC
use lib "$ENV{PG_ROOT}/lib";

use WeBWorK::PG;

# Get problem file from command line or use default
my $problem_file = $ARGV[0] || "$ENV{PG_ROOT}/t/pg_problems/blankProblem.pg";
my $seed = $ARGV[1] || 1234;

# Check if answers provided on command line (starting from ARGV[2])
my $process_answers = 0;
my $inputs_ref = {};
if (@ARGV > 2) {
    $process_answers = 1;
    # Parse answers: AnSwEr0001=value AnSwEr0002=value ...
    for my $i (2..$#ARGV) {
        if ($ARGV[$i] =~ /^AnSwEr(\d+)=(.+)$/) {
            $inputs_ref->{"AnSwEr$1"} = $2;
        } elsif ($ARGV[$i] =~ /^(\d+)=(.+)$/) {
            $inputs_ref->{"AnSwEr" . sprintf("%04d", $1)} = $2;
        }
    }
}

print "=" x 70, "\n";
print "Running PG Problem\n";
print "=" x 70, "\n";
print "Problem file: $problem_file\n";
print "Seed: $seed\n";
if ($process_answers) {
    print "Processing answers: ", join(", ", map { "$_=$inputs_ref->{$_}" } sort keys %$inputs_ref), "\n";
}
print "=" x 70, "\n\n";

# Run the PG problem
my $pg = eval {
    WeBWorK::PG->new(
        sourceFilePath => $problem_file,
        problemSeed    => $seed,
        processAnswers => $process_answers,
        inputs_ref     => $inputs_ref,
        displayMode    => 'MathJax',
        showHints      => 1,
        showSolutions  => 0,
    );
};

if ($@) {
    die "Error running problem: $@\n";
}

# Display results
print "[BODY TEXT]\n";
print "-" x 70, "\n";
print $pg->{body_text};
print "\n";

if ($pg->{head_text}) {
    print "\n[HEAD TEXT]\n";
    print "-" x 70, "\n";
    print $pg->{head_text};
    print "\n";
}

if ($pg->{errors}) {
    print "\n[ERRORS]\n";
    print "-" x 70, "\n";
    print $pg->{errors};
    print "\n";
}

if ($pg->{warnings}) {
    print "\n[WARNINGS]\n";
    print "-" x 70, "\n";
    print $pg->{warnings};
    print "\n";
}

# Show answer blanks if any
if (keys %{$pg->{answers}}) {
    print "\n[ANSWER BLANKS]\n";
    print "-" x 70, "\n";
    for my $key (sort keys %{$pg->{answers}}) {
        my $ans = $pg->{answers}{$key};
        print "$key:\n";
        if (exists $ans->{correct_ans}) {
            print "  correct_ans = $ans->{correct_ans}\n";
        }
        if (exists $ans->{student_ans}) {
            print "  student_ans = $ans->{student_ans}\n";
        }
        if (exists $ans->{score}) {
            print "  score = $ans->{score}\n";
        }
        if (exists $ans->{ans_message} && $ans->{ans_message}) {
            print "  message = $ans->{ans_message}\n";
        }
    }
}

# Show result if answers were processed
if ($process_answers && $pg->{result}) {
    print "\n[RESULT]\n";
    print "-" x 70, "\n";
    print "Score: ", $pg->{result}{score} || 0, "\n";
    if ($pg->{result}{msg}) {
        print "Message: ", $pg->{result}{msg}, "\n";
    }
}

print "\n" . "=" x 70, "\n";
print "Done\n";

