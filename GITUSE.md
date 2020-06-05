# Gitting Good Practices and common commands
**Note:** This instructions dialogue is assuming use of the Git Bash.

## Getting started
Use the following command to clone the repo to your machine, then move into the folder.
```
git clone https://github.com/arguement/Sprint-8-Sever-Side-Essentials.git
cd Sprint-8-Server-Side-Essentials
```

## File Commit Guides
Don't treat commits like simple backups - your computer does that just fine on its own. Instead, each commit should represent a completed unit of work and the system (ideally) should still be able to run after each commit. That way commits provide insight into our development progress and can be rolled back as needed

To stage files for commit, we can use the following commands
```
git add {filename}  # can optionally list multiple files OR
git add .           # stage all files for commit
```

When you're ready to commit, use the following command:
```
git commit -m "Commit Message"
```

***Note:*** The commit message should describe *what* the commit accomplishes. A good commit message sensibly completes the following sentence

> If applied, this commit will ***commit message***

Good commit messages starts with capital letters and don't end with periods (.).  
Eg. of a good commit message: `Enable registration of a user`

Hypothetically, if you prematurely made a commit and had wanted to add another file/change to it, rather than do a fresh commit, do the following
```
git add {files you want to add}
git commit --amend --no-edit
```

## Working in Branches
When you are developing a new feature(s) for the project, avoid working in master and instead checkout a new branch to work on as follows:
```
git checkout -b new-branch-name
```

Additionally, you can use `checkout` to move between different branches
```
git checkout master
```

### Merging changes to master
Once you've fully fleshed out features on the branch you want and it works appropriately, we can perform a merge to master as follows
```
git checkout master
git merge feature-branch-you-were-on
```

Ideally, this should result in a fastforward merge without conflict, as your copy of the master branch updates to include the new feature.

### Fetch, Pull and Push to the Online Repo
```
git fetch   # retrieves all new branches and files from the online repo
git pull    # fetches and attempts to merge changes from matching branch on the online repo to the current branch
```
If you wish to use a branch `git fetch` downloaded, use `git checkout branch-name` to activate it.

We need to ensure the branch we want to push has incorporated all changes with the corresponding online branch. `git pull` allows this.

Once the merge is complete (there may be conflicts that need to be resolved), the following command will push your changes.
```
git push
```

If the branch you want to push does not yet exist in the repo, use the following command:
```
git push --set-upstream origin branch-name-you-want-to-push
```