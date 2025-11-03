# Developer Information

**Workflow: Full**
Each team member creates a fork of the main repo, which they then clone locally onto their own machine. Changes are made in branches, pushing changes to their fork of the main repo. Afterwards, they create a pull request, which somebody else accepts, sending it into the main branch.

## Instructions:

### Forking:

Once you have forked your repo, run `git remote add upstream <main-repo-link>` in your terminal, setting upstream as a remote. Another remote, `origin`, is needed, but is created automatically by Git. It points to our fork on GitHub.

`git push origin <feature-branch>` pushes to your forked repo (not the main repo, our forking workflow doesn't do that). Then, from the github website, create a pull request, and let the group chat know that you made a change. Someone *else* will then come and accept it. Never accept your own pull request unless it is absolutely necessary.

`git fetch upstream` downloads all the changes from the main to your local repo. Switch to your main branch using `git switch main`, and use `git pull -rebase upstream main`. Rebase combines your code and the new code you've just pulled.

### Branches:

Before creating a new branch, always make sure your own repo is up to date by pulling.

`git checkout -b <branch-name>` creates a new branch and switches your current working directory to it. Using the commands `git branch <branch-name>` (creates new branch) and `git switch <branch-name>` (switches to branch) also works.

View all currently created branches with `git branch -a`. The current branch will be displayed with a *.

Merge finished branches back into main by first using `git switch main`, and then calling `git merge <branch-name>` from within the main branch. Once you're finished with a branch, delete it using `git branch -d <branch-name>`.

### Basic Commands:

Add files to a new commit using `git add <file-path>`, and `git commit -m "<message>"` to commit changes to your current branch.

`git status` displays the status of your branch.

### Helpful Resources:
- [Forking Workflow](https://www.atlassian.com/git/tutorials/comparing-workflows/forking-workflow)
- [About Branches](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-branches)
- [Creating Branches](https://github.com/Kunena/Kunena-Forum/wiki/create-a-new-branch-with-git-and-manage-branches)