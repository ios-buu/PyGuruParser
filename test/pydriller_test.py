from pydriller import RepositoryMining



mine = RepositoryMining("/Users/canfuu/Documents/github/openapi-directory/openapi-directory")
for commit in mine.traverse_commits():
    for mod in commit.modifications:
        if mod.old_path is not None and  mod.old_path != mod.new_path:
            print(mod.filename)
            print(mod.old_path)
            print(mod.new_path)
            print(commit.committer_date)
