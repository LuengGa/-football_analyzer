"""Main entry point for the Agentic Football Analyzer."""

import sys
from pathlib import Path

# Add src to Python path if running as module
src_path = Path(__file__).parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

def main():
    """Main entry point."""
    print("=" * 60)
    print("Agentic Football Analyzer v1.0.0")
    print("=" * 60)
    print("\nUsage:")
    print("  python -m src.cli.daemon          # Start daemon")
    print("  python -m src.cli.chat            # Interactive chat")
    print("  python -m src.cli.analyze         # Quick analysis")
    print("\nFor more information, see README.md")
    print("=" * 60)

if __name__ == '__main__':
    main()
