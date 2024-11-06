# Makefile for running Python unit tests

# Path to your Python executable (adjust if needed)
PYTHON = python3

# Directory where your test files are located (adjust if needed)
TEST_DIR = tests

# Command to run the unit tests
TEST_CMD = $(PYTHON) -m unittest discover -s $(TEST_DIR)

# Default target when 'make' is run without arguments
.PHONY: all
all: test

# Target to run the tests
.PHONY: test
test:
	$(TEST_CMD)

# Clean up any Python bytecode files (.pyc, .pyo)
.PHONY: clean
clean:
	find . -name "*.pyc" -exec rm -f {} \;
	find . -name "*.pyo" -exec rm -f {} \;
