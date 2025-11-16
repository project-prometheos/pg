# Installing Perl WeBWorK Libraries for Parity Testing

This guide will help you install the Perl WeBWorK PG libraries needed for full Perl vs Python parity comparison tests.

## Prerequisites

- Perl 5.20.3 or higher (you have 5.38.2 ✓)
- System package manager access (apt, yum, brew, etc.)

## Installation Steps

### Step 1: Install cpanminus (cpanm)

cpanminus is a lightweight Perl module installer.

**On Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install -y cpanminus
```

**On macOS (with Homebrew):**
```bash
brew install cpanminus
```

**On other systems:**
```bash
curl -L https://cpanmin.us | perl - --sudo App::cpanminus
```

### Step 2: Install Perl Dependencies

From the repository root, install all Perl dependencies:

```bash
cd /mnt/userdata/martin/GitHub/pg
cpanm --installdeps .
```

This will install all dependencies listed in `cpanfile`, including:
- DBI
- HTML::Parser
- Mojolicious
- YAML::XS
- And many more...

### Step 3: Set Up WeBWorK PG Libraries

The parity lab needs access to WeBWorK::PG modules. You have two options:

#### Option A: Use Existing Macros (Simpler)

The repository already contains PG macro files in the `macros/` directory. The Perl adapter can use these directly. Update the adapter to point to your macros:

```bash
# The adapter already looks in macros/ directory
# Just ensure the paths are correct in run_pg_snippet.pl
```

#### Option B: Install Full WeBWorK PG (More Complete)

If you want the full WeBWorK::PG::Translator environment:

1. Clone the webwork-pg repository:
```bash
cd /mnt/userdata/martin/GitHub/pg
git clone https://github.com/openwebwork/webwork-pg.git ../webwork-pg
```

2. Install webwork-pg dependencies:
```bash
cd ../webwork-pg
cpanm --installdeps .
```

3. Update `parity_lab/perl_ref/run_pg_snippet.pl` to include webwork-pg in @INC:
```perl
use lib "$FindBin::Bin/../../../webwork-pg/lib";
```

### Step 4: Verify Installation

Test that Perl can find the required modules:

```bash
perl -MWeBWorK::PG -e "print 'WeBWorK::PG loaded\n'" 2>&1 || echo "WeBWorK::PG not found (this is OK if using minimal adapter)"
```

Test the Perl adapter:

```bash
cd parity_lab
perl perl_ref/run_pg_snippet.pl tests/snippets/standard_basic.pg 42 /tmp/test_perl.json
```

### Step 5: Run Parity Tests

Once installed, run the full parity comparison tests:

```bash
source .venv/bin/activate
pytest parity_lab/tests/contract/test_parity_comparison.py -v
```

## Troubleshooting

### Issue: "cpanm: command not found"
**Solution:** Install cpanminus (see Step 1)

### Issue: "WeBWorK::PG modules not found"
**Solution:** This is OK! The adapter falls back to a minimal environment. The macros in `macros/` directory should work for most tests.

### Issue: "Can't locate macro file"
**Solution:** Check that `macros/` directory exists and update paths in `run_pg_snippet.pl` if needed.

### Issue: Permission errors during cpanm install
**Solution:** Use `--sudo` flag: `cpanm --sudo --installdeps .`

### Issue: Missing system libraries
**Solution:** Install development headers:
```bash
# Ubuntu/Debian
sudo apt-get install -y libgd-dev libdb-dev

# macOS
brew install gd
```

## Minimal Setup (Quick Start)

If you just want to test Python functionality without Perl comparison:

1. The Python tests will work without Perl
2. Tests will automatically skip Perl comparisons if Perl adapter fails
3. You can still verify Python implementation correctness

## Full Setup (For Parity Testing)

For complete Perl vs Python parity testing:

1. Install all dependencies from `cpanfile`
2. Ensure `macros/` directory is accessible
3. Optionally install full WeBWorK PG for advanced features
4. Run full test suite

## Next Steps

After installation:
1. Run `pytest parity_lab/tests/contract/test_parity_comparison.py -v`
2. Check that Perl comparisons are no longer skipped
3. Review any differences found between Perl and Python outputs

