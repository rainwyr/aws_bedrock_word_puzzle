* Model: Claude 3.5 Sonnet V2
* Permissions
    * Add S3 Full Access
    * Add Lambda Full Access
* Action Group: ag-generate-puzzle-meta
    * Function: upload_puzzle_meta_to_s3_from_json
    * Parameters: puzzle_json
* Action Group: ag-generate-puzzle-img
    * Function: generate_images_for_puzzle
    * Parameters: puzzle_id