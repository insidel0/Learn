# tests/conftest.py
import os, sys

# Add the repo root to sys.path so "src.learn...." imports work
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
