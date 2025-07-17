#!/usr/bin/env python3
"""
Setup script for inspire-demos package.

This script helps with common development tasks:
- Setting up development environment
- Installing dependencies
- Running tests
- Building the package
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


def run_command(cmd, description=""):
    """Run a shell command and handle errors"""
    if description:
        print(f"Running: {description}")
    
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        if e.stderr:
            print(e.stderr)
        return False


def setup_dev_environment():
    """Set up development environment"""
    print("Setting up development environment...")
    
    commands = [
        ("python -m pip install --upgrade pip", "Upgrading pip"),
        ("pip install -e .[dev]", "Installing package in development mode"),
        ("pre-commit install", "Installing pre-commit hooks"),
    ]
    
    for cmd, desc in commands:
        if not run_command(cmd, desc):
            return False
    
    print("Development environment setup complete!")
    return True


def run_tests():
    """Run the test suite"""
    print("Running tests...")
    return run_command("pytest", "Running test suite")


def run_linting():
    """Run code quality checks"""
    print("Running code quality checks...")
    
    commands = [
        ("black --check src/ examples/ tests/", "Checking code formatting"),
        ("flake8 src/ examples/ tests/", "Running linting"),
        ("mypy src/", "Running type checking"),
    ]
    
    all_passed = True
    for cmd, desc in commands:
        if not run_command(cmd, desc):
            all_passed = False
    
    return all_passed


def format_code():
    """Format code with black"""
    print("Formatting code...")
    return run_command("black src/ examples/ tests/", "Formatting code with Black")


def build_package():
    """Build the package"""
    print("Building package...")
    
    # Clean previous builds
    run_command("rm -rf dist/ build/ *.egg-info/", "Cleaning previous builds")
    
    return run_command("python -m build", "Building package")


def install_package():
    """Install the package"""
    print("Installing package...")
    return run_command("pip install -e .", "Installing package in development mode")


def main():
    parser = argparse.ArgumentParser(description="Setup script for inspire-demos")
    parser.add_argument("--setup", action="store_true", help="Set up development environment")
    parser.add_argument("--test", action="store_true", help="Run tests")
    parser.add_argument("--lint", action="store_true", help="Run linting and type checking")
    parser.add_argument("--format", action="store_true", help="Format code")
    parser.add_argument("--build", action="store_true", help="Build package")
    parser.add_argument("--install", action="store_true", help="Install package")
    parser.add_argument("--all", action="store_true", help="Run setup, test, lint, and build")
    
    args = parser.parse_args()
    
    if not any(vars(args).values()):
        parser.print_help()
        return
    
    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    success = True
    
    if args.setup or args.all:
        success &= setup_dev_environment()
    
    if args.install:
        success &= install_package()
    
    if args.format:
        success &= format_code()
    
    if args.lint or args.all:
        success &= run_linting()
    
    if args.test or args.all:
        success &= run_tests()
    
    if args.build or args.all:
        success &= build_package()
    
    if success:
        print("All operations completed successfully!")
    else:
        print("Some operations failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
