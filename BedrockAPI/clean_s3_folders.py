import boto3

def clean_s3_folders(bucket_name="word-puzzle-421", folders=None):
    if folders is None:
        folders = ["images/", "puzzles/", "solutions_by_id/", "solutions_by_images/"]

    s3 = boto3.client("s3")
    s3_resource = boto3.resource("s3")
    bucket = s3_resource.Bucket(bucket_name)

    deleted_files = []

    for folder in folders:
        print(f"🔍 Scanning folder: {folder}")
        objects_to_delete = [{"Key": obj.key} for obj in bucket.objects.filter(Prefix=folder)]

        if objects_to_delete:
            print(f"🧹 Deleting {len(objects_to_delete)} files from {folder}...")
            s3.delete_objects(
                Bucket=bucket_name,
                Delete={"Objects": objects_to_delete}
            )
            deleted_files.extend([obj["Key"] for obj in objects_to_delete])
        else:
            print(f"✅ Folder {folder} is already empty.")

    print(f"\n🧼 Cleanup complete. Total files deleted: {len(deleted_files)}")
    return deleted_files

clean_s3_folders()