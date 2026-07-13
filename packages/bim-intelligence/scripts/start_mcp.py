"""
Arranca el MCP server BIM en modo stdio para Claude Code.

    python scripts/start_mcp.py

Agregar a ~/.claude/settings.json:
{
  "mcpServers": {
    "construdata-bim": {
      "command": "python",
      "args": ["scripts/start_mcp.py"],
      "cwd": "C:/Users/HP/Desktop/optimizacion para negocios en el atlantico/tubara/construdata/packages/bim-intelligence"
    }
  }
}
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parents[2] / ".env")

from mcp.server import main as run_mcp

if __name__ == "__main__":
    from bim_intelligence.mcp.server import main
    main()
