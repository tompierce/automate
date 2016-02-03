# AuTOMate

## Intro

AuTOMate is an attempt to create a light-weight automation/continous integration server in Python. 
It's inspired by Jenkins/Hudson and borrows a lot of it's terminology from them.
The mission is to make automation simple to use, and tightly integrated with version control.

## Benefits

* **File based configuration only** - GUIs tend to generate ugly config files which are difficult to manage in source control. AuTOMate only uses json config.

* **Easily extensible** - It's written in python and allows you to drop additional scripts in to add more triggers/actions.

* **Easy to compose actions into large jobs/pipelines** - It's being designed to make it easy to add, modify and re-use actions across multiple jobs/pipelines. **(NOT YET)**

## Is it ready to be used in the wild?

**No. Definitely not. But if you'd like to take the plunge and do some early alpha testing, that would be great!**
