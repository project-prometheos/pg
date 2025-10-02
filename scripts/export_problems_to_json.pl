#!/usr/bin/env perl

=head1 NAME

export_problems_to_json.pl - Export problem metadata to JSON for database import

=head1 SYNOPSIS

    perl scripts/export_problems_to_json.pl [problem_directory] [output_file]

=head1 DESCRIPTION

This script uses the existing SampleProblemParser to extract metadata from PG files
and exports it to JSON format for consumption by the Python import script.

=cut

use strict;
use warnings;
use experimental 'signatures';
use feature 'say';
use JSON::PP;
use FindBin;
use lib "$FindBin::Bin/../lib";

use SampleProblemParser qw(generateMetadata);

# Get arguments
my $problem_dir = $ARGV[0] // "$FindBin::Bin/../tutorial/sample-problems";
my $output_file = $ARGV[1] // "$FindBin::Bin/../problems_metadata.json";

say "WeBWorK Problem Metadata Export";
say "=" x 50;
say "Problem directory: $problem_dir";
say "Output file: $output_file";
say "";

# Generate metadata using existing parser
say "Parsing PG files...";
my $metadata = generateMetadata($problem_dir, verbose => 0);

my $problem_count = scalar(keys %$metadata);
say "Found $problem_count problems";

# Export to JSON
say "Exporting to JSON...";
open my $fh, '>:encoding(UTF-8)', $output_file 
    or die "Could not open '$output_file': $!";

my $json = JSON::PP->new->utf8->pretty->canonical;
print $fh $json->encode($metadata);
close $fh;

say "✓ Successfully exported metadata to $output_file";
say "";
say "Next step: python scripts/import_problems.py";

1;
