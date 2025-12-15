To run a demo and view the synchronized data in Surrealist, follow these
  steps:

  1. Start the CoreText Daemon
  First, ensure the database is running.

   1 poetry run coretext start

  2. Install Git Hooks (If not already done)
  Ensure the synchronization hooks are active in your repository.

   1 poetry run coretext install-hooks

  3. Trigger Synchronization via Git
  The synchronization happens automatically when you commit Markdown files.
  Create a test file and commit it.

   1 # Create a dummy file
   2 echo "# Demo File\n\nThis is a test file for CoreText." > demo.md
   3 
   4 # Stage and commit (this triggers the hooks)
   5 git add demo.md
   6 git commit -m "Add demo file for CoreText sync"

  4. Open and Configure Surrealist
   1. Open Surrealist: Download and open the Surrealist
      (https://surrealist.app/) application (or use the web version).
   2. Connect:
       * Endpoint: ws://localhost:8000/rpc (or http://localhost:8000/rpc)
       * Namespace: coretext
       * Database: coretext
       * Authentication:
           * User: root
           * Password: root

  5. View the Data
  In the Query view of Surrealist, run the following SQL queries to verify the
  data:

  View All Files:
   1 SELECT * FROM file;

  View All Headers:
   1 SELECT * FROM header;

  View All Nodes (Files + Headers):
   1 SELECT * FROM type::table($table) WHERE $table IN ['file', 'header'];
  (Or simply browse the tables in the left sidebar explorer)

  You should see an entry for demo.md in the file table and a corresponding
  entry for "Demo File" in the header table.\n\nAnother change
\n\nAnother change
\n\nAnother change
\n\nOne more change
\n\nYet another change.

## New Demo Section
This content is synced via Git hook.

# Retry Sync
 Testing schema fix.

# Final Verify
 Should work now.

# Success
 This should sync perfectly.

# test  
test

# Another Test
 This should finally sync.

# Full Graph Test

# Fixes Applied:
  1. Schema Alignment: Added missing content, content_hash, level to schema and models. Mapped datetime to string.
  2. Edge Constraints: Removed FROM node TO node constraint from relation tables to allow flexible ID matching. Removed mandatory order field
    from contains.
  3. GraphManager Logic:
      * Switched to backticks for complex IDs (e.g., node:`demo.md`).
      * Implemented robust Upsert logic using UPSERT for nodes.
      * Implemented robust Relation logic using RELATE for edges (instead of UPSERT which failed on relation tables).
      * Correctly formats in/out pointers with table prefixes.
      * Added error checking for transaction results.