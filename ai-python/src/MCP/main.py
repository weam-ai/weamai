from server import mcp
def main():
    tool_imports = {
        'gmail': lambda: __import__('google.gmail.gmail_tools'),
        'drive': lambda: __import__('google.gdrive.drive_tools'),
        'calendar': lambda: __import__('google.gcalendar.calendar_tools'),
    }
    tool_icons = {
        'gmail': '📧',
        'drive': '📁',
        'calendar': '📅',
    }
    for tool in tool_imports.keys():
        tool_imports[tool]()
    mcp.run(transport='sse')
    

if __name__ == "__main__":
    # Initialize and run the server
    main()