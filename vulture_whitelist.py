# Whitelist for vulture to ignore false positives
# These functions are used by Typer CLI decorators

main  # Used as @app.callback()
refactor_plan  # Used as @app.command()
watch  # Used as @app.command()
unused  # Used as @app.command()
init  # Used as @app.command()

# These are part of data models and configuration classes
line_start
line_end
related_files
project_structure
dependencies
enable_ai_suggestions
max_file_size
cache_results
cache_ttl
max_line_length
complexity_threshold
version

# These are part of enum definitions
EXACT
RENAMED
MODIFIED
SEMANTIC

# These are callback parameters
frame
sig

# These are methods that are part of interfaces or may be used dynamically
analyze_file
CloneType
calculate_similarity
_cleanup_expired_cache
_detect_duplicate_code
get_language_config
get_analysis_thresholds
get_output_config
on_modified
on_created
on_deleted
_last_analysis