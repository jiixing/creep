Creep README file
=================

Overview
--------

Creep is an incremental deploy tool, allowing delta update from a Git
repository or a regular directory into a FTP or SSH remote server. It allows
deployment of any application where files needed on target servers (e.g.
production) match files in your repository, meaning it works well with pure
front-end websites using HTML/CSS/JS or server technologies like PHP.

Projects deployed through Creep should provide configuration file(s) to define
_environments_ which are the different locations where deployment should happen
(e.g. integration servers, production servers, etc.), and optional _modifiers_
which describe how to transform files before sending them (e.g. compile,
minify, obfuscate, etc.).

Deployments are incremental and Creep keeps track of deployed snapshots on
all target environments so that only changed files are send next time. This
tracking mechanism depends on the type of repository used, for exemple Creep
uses revision hashes when deploying from a Git repository to allow easy diffs.

Installing
----------

To install Creep, checkout repository somewhere and create a symbolic link in
your `$PATH` to main executable file `creep.py` (located in `src` directory).
While this is not mandatory (you can prefer to call Creep using full path to
`creep.py`) it's surely more convenient.

    $ cd creep
    $ sudo ln -s src/creep.py /usr/bin/creep
    $ creep -h # display help

Once Creep is installed go to your project folder and follow next section to
create a your first environment configuration file.

Environments
------------

Environments are named locations pointing to the servers you'll want to deploy
your project to. They must be specified in a JSON file named `.creep.envs` and
located inside the directory which contains the file you want to deploy. This
directory will be used as the root for your deployment meaning that all files
it contains will be deployed to targer destination, preserving the same
hierarchical structure. You can use a sub-directory inside your project as your
deployment root (e.g. the `src` folder in your Git repository) so you only
deploy its content. You can also support multiple deployment configurations for
a single project by having more than one environment file in different folders
(e.g. one in your `src` folder to deploy server code, and another one in
`assets` to deploy static files to different servers).

Here is what an environments configuration file looks like:

    {
        "default": {
            "connection": "file:///home/www-data/my-project/"
        },
        "integration": {
            "connection": "ftp://me:password@my-dev-server/www-data/"
        },
        "production": {
            "connection": "ssh://login@my-prod-server.com/www-data/"
        }
    }

Each location (`default`, `integration` and `production` in this example) must
specify a connection string defining a protocol and optional address,
credentials and/or path. Creep can currently deploy through local file system,
FTP or SSH, and some extra options may be specified depending on the protocol
; see below for details about protocols and options.

Once environments configuration file is ready you can start using Creep. Just
type `creep <env>` (or full path to `creep.py` if you didn't add it to your
`$PATH`) where `<env>` is target environment name. When not specified,
environment `default` is used:

    $ creep

Creep will then connect to target environment and try to retrieve information
from last deployment to compute incremental tasks. When you deploy for the
first time this information won't be available and Creep will ask you if a
full deploy should be performed instead. After each successful deployment it
will save information on target environment in a `.creep.revs` file.

While storing deployment information on target environment keeps related data
altogether and works even if you're not the only one performing deployments,
you may prefer to store them locally instead. In that case just add a new
`local` option with value `true` for all affected environments in your
`.creep.envs` file:

    {
        ...
        "integration": {
            "connection": "ftp://me:password@my-dev-server/www-data/",
            "local": true
        },
        ...
    }

You can specify additional options depending on the protocol you're using. To
specify options just add an "options" property containing required options as a
JSON object:

    {
        "default": {
            "connection": "ssh://www-data@localhost/www.mywebsite.com/",
            "options": {
                "extra": "-o StrictHostKeyChecking=no"
            }
        }
    }

Here are the supported protocols, expected connection string and available
options for each of them:

- Local FS:
  - Use `file://path` where path is relative to current directory (note the
    triple `/` in example above to get an absolute path).
- FTP:
  - Use `ftp://user:pass@host:port/path` where `user` and `pass` are optional
    credentials (anonymous login will be used if they're missing), `port` is an
    optional FTP port which defaults to 21, and `path` is a path relative to FTP
    user home directory.
  - Boolean option "passive" enables (default) or disables passive mode.
- SSH:
  - Use `ssh://user@host:port/path` where variables are similar to the ones used
    for FTP deployment. Password can't be specified here, so you'll need to
    either enter password manually or setup SSH keys and start SSH agent.
  - String option "extra" can be used to pass additional parameters to SSH
    command. 

Modifiers
---------

Modifiers allow you to declare special behaviors that should be triggered on
some files before they're send to target environment. Creep supports three
different kinds of modifiers:

- _name_ modifiers can change the name of a file using regular expression
  search/replace ;
- _adapt_ modifiers can change the content of a file using a custom shell
  command ;
- _link_ modifiers can link one or more files together so they're evaluated
  when their parent file is changed.

Modifiers must be specified in a JSON file named `.creep.mods` located in the
same folder(s) than your environment configuration file(s). Each file specifies
a list of rules which apply to all files matching a given regular expression and
contain optional _name_, _adapt_ or _link_ modifiers.

Here is what a modifiers configuration file looks like:

    [
        {
            "pattern": "\\.min\\.js$"
        },
        {
            "pattern": "\\.js$",
            "adapt": "uglifyjs --compress --mangle -- '{}'"
        },
        {
            "pattern": "(.*)\\.less$",
            "adapt": "lessc --clean-css '{}'",
            "name": "\\1.css"
        }
    ]

Each rule must specify matched files using a regular expression in `pattern`
property (remember that backslashes must be escaped in JSON) Rules are
evaluated in sequence and each file can only match one single rule (evaluation
stops on the first matched pattern). Other (optional) properties are applied on
files matching given pattern, if any.

- `name` property specifies new name for file and supports back references on
  the regular expression used in `pattern`. In the example above, files ending
  with `.less` (matching `(.*)\.less$`) will have their extension changed to
  `.css` (the back reference `\\` captured original file name without extension
  in associated pattern).
- `adapt` property specifies a shell command to be executed after replacing
  special `{}` sequence by path to file being matched. Output of this command
  will replace content of the file before it's sent to environment. In the
  example above executable `uglifyjs` is called to minify JavaScript files
  (maching `\.js$`). Note presence of first rule which matches files whose name
  ends with `.min.js`: it doesn't specify any action but prevents the other
  `\.js$` rule from being triggered as it's evaluated before. In this example,
  it prevents modified JavaScript files from being modified another time.
- `link` property specifies a shell command similar to the one for `adapt`
  property, but this one should return path (relative to deployment directory)
  to all files that should be sent whenever matched ones are matched.

Troubleshooting
---------------

This project is still under develpement and may not behave as you would expect.
The `-v` (verbose) switch may help you understanding how your environments and
modifiers files are used in case of issue.

If you really can't figure out what's happening, don't hesitate to contact me!
