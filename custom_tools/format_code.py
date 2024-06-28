from pathlib import Path
from time import time
import re
import subprocess

AUTO_FORMAT = True
match_lua = re.compile(r"([ \t]*)```lua\n(.*?)```", re.DOTALL)
output_folder = Path(f"output_{int(time())}")
output_folder.mkdir()

pathlist = Path("../").rglob("*.md")
for path in pathlist:
    with path.open("r") as file:
        content = file.read()

    new_content = content
    offset = 0

    for count, match in enumerate(match_lua.finditer(content)):
        # Extract Lua code
        spaces = match.group(1)
        lua = match.group(2)

        # Create output file path
        output_path = output_folder / f"{path.stem}_{count}.luau"

        with output_path.open("w") as output:
            if not lua.isascii():
                print("non-ascii", output_path)
            if ";" in lua:
                print("semicolons", output_path)
            output.write(lua)

        # Format Lua code if AUTO_FORMAT is True
        if AUTO_FORMAT:
            try:
                subprocess.run(
                    ["stylua", str(output_path)],
                    check=True,
                )

                with output_path.open("r") as output:
                    formatted_lua = output.read()
                    if spaces:
                        formatted_lua_lines = formatted_lua.split("\n")
                        for index, line in enumerate(formatted_lua_lines):
                            if line != "":
                                formatted_lua_lines[index] = spaces + line
                        formatted_lua = "\n".join(formatted_lua_lines) + spaces

                    # Calculate new positions
                    start = match.start(2) + offset
                    end = match.end(2) + offset
                    new_content = new_content[:start] + formatted_lua + new_content[end:]

                    # Adjust offset for next replacement
                    offset += len(formatted_lua) - (end - start)
            except:
                pass

    # Write the modified content back to the file if changes were made
    if AUTO_FORMAT and content != new_content:
        with path.open("w") as file:
            file.write(new_content)
