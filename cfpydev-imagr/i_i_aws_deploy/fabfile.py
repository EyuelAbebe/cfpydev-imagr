from fabric.api import run, env, local
from fabric.api import prompt, execute, sudo
from fabric.contrib.project import rsync_project
from fabric.contrib.files import upload_template
import boto.ec2
import time
import os

cwd_ = os.getcwd()

env.hosts = ['localhost', ]
env.aws_region = 'us-west-2'
env.key_filename = '/Users/eyuelabebe/.ssh/mykeypair.pem'


def host_type():
    run('uname -s')


def get_ec2_connection():
    if 'ec2' not in env:
        conn = boto.ec2.connect_to_region(env.aws_region)
	if conn is not None:
	    env.ec2 = conn
	    print "Connected to EC2 region %s" % env.aws_region
	else:
	    msg = "Unable to connect to EC2 region %s"
	    raise IOError(msg % env.aws_region)
    return env.ec2

def provision_instance(wait_for_running=False, timeout=60, interval=2):
    wait_val = int(interval)
    timeout_val = int(timeout)
    conn = get_ec2_connection()
    instance_type = 't1.micro'
    key_name = 'mykeypair'
    security_group = 'ssh-access'
    image_id = 'ami-ddaed3ed'

    reservations = conn.run_instances(image_id, key_name=key_name, instance_type=instance_type, security_groups=[security_group, ],)
    new_instances = [i for i in reservations.instances if i.state == u'pending']
    running_instance = []
    if wait_for_running:
        waited = 0
    while new_instances and (waited < timeout_val):
	    time.sleep(wait_val)
	    waited += int(wait_val)
	    for instance in new_instances:
	        state = instance.state
		print "Instance %s is %s" % (instance.id, state)
		if state == "running":
		    running_instance.append(new_instances.pop(new_instances.index(i)))
		instance.update()

def list_aws_instances(verbose=False, state='all'):
    conn = get_ec2_connection()
    reservations = conn.get_all_reservations()
    instances = []
    for res in reservations:
        for instance in res.instances:
            if state == 'all' or instance.state == state:
                instance = {
                    'id': instance.id,
                    'type': instance.instance_type,
                    'image': instance.image_id,
                    'state': instance.state,
                    'instance': instance,
                }
                instances.append(instance)
    env.instances = instances
    if verbose:
        import pprint
        pprint.pprint(env.instances)



def select_instance(state='running'):
    if env.get('active_instance', False):
        return

    list_aws_instances(state=state)

    prompt_text = "Please select from the following instances:\n"
    instance_template = " %(ct)d: %(state)s instance %(id)s\n"
    for idx, instance in enumerate(env.instances):
        ct = idx + 1
        args = {'ct': ct}
        args.update(instance)
        prompt_text += instance_template % args
    prompt_text += "Choose an instance: "

    def validation(input):
        choice = int(input)
        if not choice in range(1, len(env.instances) + 1):
            raise ValueError("%d is not a valid instance" % choice)
        return choice

    choice = prompt(prompt_text, validate=validation)
    env.active_instance = env.instances[choice - 1]['instance']


def db_envs():
    with open('credentials.txt') as f:
        return str(f.read().rstrip())


def run_command_on_selected_server(command):
    select_instance()
    selected_hosts = ['ubuntu@' + env.active_instance.public_dns_name]
    execute(command, hosts=selected_hosts)


def _install_nginx():
    sudo('apt-get install nginx')
    sudo('/etc/init.d/nginx start')


def install_nginx():
    run_command_on_selected_server(_install_nginx)


def stop_instance():
    select_instance()
    env.ec2.stop_instances(instance_ids=[env.active_instance.id])

def terminate_instance():
    select_instance(state='stopped')
    env.ec2.terminate_instances(instance_ids=[env.active_instance.id])


def run_deploy():
    local('ssh-add ~/.ssh/mykeypair.pem')
    install_nginx()
    sudo('apt-get update')
    sudo('apt-get install -y supervisor')
    sudo('apt-get install -y python-pip')
    sudo('apt-get install -y libpq-dev')
    sudo('apt-get install -y python-dev')
    sudo('apt-get install -y libjpeg62 libjpeg62-dev zlib1g-dev')
    rsync_project(local_dir='/Users/eyuelabebe/Desktop/projects/django-imagr/cfpydev-imagr', remote_dir='~/')
    sudo('pip install -r cfpydev-imagr/requirements.txt')
    upload_template('simple_nginx_config', '~/',  context={'host_dns': env.active_instance.public_dns_name})
    upload_template('supervisord.conf', '~/', context={'host_envs': db_envs()})
    sudo('mv supervisord.conf /etc/supervisor/conf.d/cfpydev-imagr.conf')
    sudo('mv /etc/nginx/sites-available/default /etc/nginx/sites-available/default.orig')
    sudo('mv simple_nginx_config /etc/nginx/sites-available/default')
    sudo('/etc/init.d/nginx restart')
    sudo('/etc/init.d/supervisor stop')
    sudo('/etc/init.d/supervisor start')


def run_ssh():
    select_instance()
    local('ssh -i /Users/eyuelabebe/.ssh/mykeypair.pem ubuntu@{}'.format(env.active_instance.public_dns_name))

def ssh():
    run_command_on_selected_server(run_ssh)

def deploy():
    run_command_on_selected_server(run_deploy)


