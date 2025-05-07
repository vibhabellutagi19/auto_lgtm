from typing import Dict, List, Any
import argparse
import sys
from common.rich_logger import RichLogger
from rich.table import Table
from lgtm import review_pr


def main():
    logger = RichLogger()
    
    try:
        logger.print_title("Auto LGTM", "Automated Code Review")
        
        # Parse command line arguments
        parser = argparse.ArgumentParser(description="Auto LGTM - Automated Code Review")
        parser.add_argument("--repo", type=str, required=True, help="Repository name")
        parser.add_argument("--pr", type=int, required=True, help="Pull request number")
        parser.add_argument("--project-id", type=str, required=True, help="Google Cloud project ID")
        args = parser.parse_args()

        repo: str = args.repo
        pr_number: int = args.pr
        project_id: str = args.project_id
        
        # Display PR details
        pr_table = Table(title="Pull Request Details")
        pr_table.add_column("Property", style="cyan")
        pr_table.add_column("Value", style="green")
        pr_table.add_row("Repository", repo)
        pr_table.add_row("PR Number", str(pr_number))
        pr_table.add_row("Project ID", project_id)
        logger.console.print(pr_table)

        review_pr(repo, pr_number, project_id)
        
    except Exception as e:
        logger.print_error(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 