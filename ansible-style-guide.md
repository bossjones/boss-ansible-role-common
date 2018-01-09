_draft_
# Ansible Style Guide

## General

- YAML files - All yaml files should use 2 space indents and end with .yml
- Variables - Use jinja variable syntax over deprecated variable syntax. {{ var }} not $var
- Use spaces around jinja variable names. {{ var }} not {{var}}
- Variables that are environment specific and that need to be overridden should be in ALL CAPS.
- Variables that are internal to the role should be lowercase.
- Prefix all variables defined in a role with the name of the role. Example: EDXAPP_FOO
- Keep roles self contained - Roles should avoid including tasks from other roles when possible
- Plays should do nothing more than include a list of roles except where pre_tasks and post_tasks are required (to manage a load balancer for example)
- Plays/Playbooks that apply to the general community should be copied to configuration/playbooks
- Plays/Playbooks that apply only to a specific organization (edx-east, edx-west) should be copied to a sub-directory under configuration/playbooks
- Tests - For automated integration tests use an included play named test.yml is included and run when a run_tests var is set to validate the role installation on a single instance.
- Deploys - For application updates include a deploy.yml with a list of tasks that start with service stop and end with a service start that is run to deploy an application update. Every task in deploy.yml should be tagged with deploy
- Nothing outside of tasks in deploy.yml should affect the application state
- All tasks in deploy.yml should be able to run as a user with limited sudo rule and not require root access.
- Handlers - Every role should have one or more handlers for restarting the service(s), for tasks that run in main.yml that require service restarts they/it will be notified.
- Separators - Use underscores (e.g. my_role) not dashes (my-role).
- Paths - When defining paths, do not include trailing slashes (e.g. my_path: /foo not my_path: /foo/. When concatenating paths, follow the same convention (e.g. {{ my_path }}/bar not {{ my_path }}bar)

## Ansible version
- use the latest Ansible version available via pip

## Types

Ansible does not really care about types. However booleans are an exception. Ansible will accept booleans in several forms:

```
create_key: yes
needs_agent: no
knows_oop: True
likes_emacs: TRUE
uses_cvs: false
```

But Ansible will set booleans in Python convention True / False in templates. To avoid confusion booleans should also be set in variable files with Python convention True / False. When another boolean form in an template is needed Jinja filter should be applied:

```
{{ boolean_variable | lower }}
{{ boolean_variable | upper }}
```

## Conditionals and Return Status

- Always use when: for conditionals - To check if a variable is defined when: my_var is defined or when: my_var is not defined
- To verify return status (see conditionals)

     - command: /bin/false
        register: my_result
        ignore_errors: True
      - debug: msg="task failed"
        when: my_result|failed

## Formatting

- Break long lines using yaml line continuation.
- Reference: http://docs.ansible.com/playbooks_intro.html

_incorrect_
```yaml
  - file: dest="{{ test }}" src="./foo.txt" mode=0077 state=present user="root" group="wheel"
```
_incorrect_
```yaml
- file: >
	dest="{{ test }}"
	src="./foo.txt"
	mode=0077
	state=present
	user="root"
	group="wheel"
```
_correct_
```
  - file:
      dest: "{{ test }}"
	  src: "./foo.txt"
	  mode: 0077
	  state: present
	  user: "root"
	  group: "wheel"
```
## Modules

- use offical modules where possible
- modules are listed on the [Ansible website](http://docs.ansible.com/ansible/modules_by_category.html)
_incorrect_
```yaml
- name: Configure vm.vfs_cache_pressure
  lineinfile: dest=/etc/sysctl.conf line="vm.vfs_cache_pressure = {{ swapfile_vfs_cache_pressure }}" regexp="^vm.vfs_cache_pressure[\s]?=" state=present
  notify: Reload sysctl
  when: swapfile_vfs_cache_pressure != false
```
_correct_
```yaml
- name: Configure vm.vfs_cache_pressure
  sysctl:
    name: vm.vfs_cache_pressure
	value: "{{ swapfile_vfs_cache_pressure }}"
	state: present
	sysctl_file: /etc/sysctl.conf
```

## Roles
### Role Variables

- group_vars/all - Contains variable definitions that apply to all roles.
- "common" role - Contains variables and tasks that apply to all roles that are edX specific.
- Roles variables - Variables specific to a role should be defined in /vars/main.yml. All variables should be prefixed with the role name.
- Role defaults - Default variables should configure a role to install edx in such away that all services can run on a single server
- Variables that are environment specific and that need to be overridden should be in all caps.
- Every role should have a standard set of role directories, example that includes a python and ruby virtualenv:
```yaml
    edxapp_data_dir: "{{ COMMON_DATA_DIR }}/edxapp"
    edxapp_app_dir: "{{ COMMON_APP_DIR }}/edxapp"
    edxapp_log_dir: "{{ COMMON_LOG_DIR }}/edxapp"
    edxapp_venvs_dir: "{{ edxapp_app_dir }}/venvs"
    edxapp_venv_dir: "{{ edxapp_venvs_dir }}/edxapp"
    edxapp_venv_bin: "{{ edxapp_venv_dir }}/bin"
    edxapp_rbenv_dir: "{{ edxapp_app_dir }}"
    edxapp_rbenv_root: "{{ edxapp_rbenv_dir }}/.rbenv"
    edxapp_rbenv_shims: "{{ edxapp_rbenv_root }}/shims"
    edxapp_rbenv_bin: "{{ edxapp_rbenv_root }}/bin"
    edxapp_gem_root: "{{ edxapp_rbenv_dir }}/.gem"
    edxapp_gem_bin: "{{ edxapp_gem_root }}/bin"
```
### Role Naming Conventions

- Role names - Terse, one word if possible, use underscores if necessary.
- Role task names - Terse, descriptive, spaces are OK and should be prefixed with the role name.
- Role handlers - Terse, descriptive, spaces are OK and should be prefixed with the role name

## Secure vs. Insecure data

As a general policy we want to protect the following data:

- Usernames
- Public keys (keys are OK to be public, but can be used to figure out usernames)
- Hostnames
- Passwords, API keys

Directory structure for the secure repository:

ansible
├── files
├── keys
└── vars

The default secure_dir is set in group_vars/all and can be overridden by adding another file in group_vars that corresponds to a deploy group name.

For templates or files that are secure use first_available_file, example:
```yaml
- name: xserver | install read-only ssh key for the content repo that is required for grading
  copy: src={{ item }} dest=/etc/git-identity force=yes owner=ubuntu group=adm mode=60
  first_available_file:
    - "{{ secure_dir }}/files/git-identity"
    - "git-identity-example"
```

## Sources

[Wikipedia YAML](https://en.wikipedia.org/wiki/YAML)
[Ansible documentation YAML Syntax](http://docs.ansible.com/ansible/YAMLSyntax.html)
[openshift Ansible Styleguide](https://github.com/openshift/openshift-ansible/blob/master/docs/style_guide.adoc)
[Open edX Ansible Styleguide](https://openedx.atlassian.net/wiki/display/OpenOPS/Ansible+Code+Conventions)
