from pydriller import RepositoryMining

#

mine = RepositoryMining("https://github.com/APIs-guru/openapi-directory.git")
print(1)
for commit in mine.traverse_commits():
    print(commit.hash)
    for modification in commit.modifications:
        print(f'Filename {modification.filename}')
        print(f'Path {modification.new_path}')
        print(f'Diff: {modification.diff}')
# Total commits: 4005, Commits touching Java: 2631
