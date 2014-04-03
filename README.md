kap10
=====

A small deployment system. It essentially runs arbitrary commands

Currently used to deploy Projecto.

Screenies
---------

![Main Screen](https://raw.github.com/shuhaowu/kap10/master/main.png)

-----------

![Deploy Screen](https://raw.github.com/shuhaowu/kap10/master/deploy.png)


database.json format
--------------------

Kap10 deployment
----------------

Kap10 is capable of deploying itself. However, it needs to be deployed once via
a fabric file before it can be deployed.

For the vagrant box the deployment goes as follows:

    $ cp configs database.json.dst database.json # you might need to modify things in monit, nginx as well.
    $ vagrant up
    $ wget https://raw.githubusercontent.com/mitchellh/vagrant/master/keys/vagrant
    $ fab deploy --host 192.168.33.155 --user vagrant -i vagrant
    $ fab setup --host 192.168.33.155 --user vagrant -i vagrant
    $ vagrant ssh
    $ sudo vim /etc/monit/monitrc # change it so that "set httpd port 2812" is uncommented and allow localhost
    $ sudo service monit restart
    $ sudo monit start all
    $ sudo service nginx start

