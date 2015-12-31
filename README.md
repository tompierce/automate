# AuTOMate

## Intro

AuTOMate is an attempt to create a light-weight automation/continous integration server. It's inspired by Jenkins/Hudson but with a few twists.

## Benefits

* **File based configuration only** - GUIs tend to generate ugly config files which are difficult to manage in source control. AuTOMate only uses json config.

* **Easily extensible** - It's written in python and will allow (**NOT YET!**) you to drop additional scripts in to add more triggers/actions.

* **Easy to compose actions into large jobs/pipelines** - It's being designed to make it easy to add, modify and re-use actions across multiple jobs/pipelines.

## Is it ready to be used in the wild?

**No. Definitely not.**
