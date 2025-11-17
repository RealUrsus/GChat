#!/usr/bin/env python3
"""
Test script for conversation sources
Tests the new conversation source abstractions without requiring API keys
"""

import sys
from conversation_sources import FileConversationSource

def test_file_source():
    """Test file conversation source."""
    print("Testing FileConversationSource...")
    print("=" * 60)

    # Test with normal conversation file
    file_path = "payloads/normal_conversation.txt"
    source = FileConversationSource(file_path)

    print(f"Total messages: {source.get_total_count()}")
    print(f"Has messages: {source.has_messages()}")
    print()

    print("Messages:")
    for i, message in enumerate(source.get_messages(), 1):
        print(f"  [{i}] {message}")

    print()
    print(f"After iteration - Has messages: {source.has_messages()}")
    print(f"Current index: {source.get_current_index()}")

    # Test reset
    print("\nTesting reset...")
    source.reset()
    print(f"After reset - Current index: {source.get_current_index()}")
    print(f"After reset - Has messages: {source.has_messages()}")

    print("\n✅ FileConversationSource test passed!")
    print("=" * 60)

def main():
    """Run tests."""
    print("\n🧪 Running conversation source tests\n")

    try:
        test_file_source()
        print("\n✅ All tests passed!")
        return 0
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
