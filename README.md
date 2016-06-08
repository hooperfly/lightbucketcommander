# Light Bucket Commander
![Alt Zack and IoB Wall](doc/images/lbc_banner.png?raw=true "Zack and IoB Wall")

## Version:
This is beta version 0.0.3 of the Light Bucket Commander(LBC) and subject to major refactoring.

## Overview:
The Light Bucket Commander(LBC) is a web based, RESTful application for controlling multiple 
light buckets including the [IoB 2016 Project](https://github.com/breedx2/IoB2016).

    usage: lbc.py [-h] [-i IP] [-p PORT] [-f FILE] [-g] [-c] [-t] [-v]

    optional arguments:
      -h, --help            show this help message and exit
      -i IP, --ip IP        ip address
      -p PORT, --port PORT  port number
      -f FILE, --file FILE  use the specified client configuration file
      -g, --generate        generate a client configuration stub
      -c, --curl            dump actions as curl commands
      -t, --test            test mode; do not send curl commands
      -v, --verbose         verbose mode

The default values for `IP`, `PORT`, and `FILE`, if not specified, are `127.0.0.1`, `5000`, and `lbc_conf.xml`, respectively.

### Running the Light Bucket Commander
Open a terminal window and type the following command:

    $ python lbc.py -v -c -i <ip_address>

    where <ip_address> is the IP address of the machine running the server.
    If the -i option is not used, the IP address defaults to 127.0.0.1 (i.e. localhost)

LBC is a python based `Flask` application. Please reference the [Flask documentation](http://flask.pocoo.org/docs/0.10/)
for the installation and usage of `Flask`. Here are some of the python packages(versions) needed by `Flask`:

- Flask (0.10.1)
- itsdangerous (0.24)
- Jinja2 (2.8)
- Werkzeug (0.11.3)

On startup, the LBC reads the main LBC configuration file `conf.xml`. 
Configuration data contained in the `conf.xml` is used to initialize the LBC server. 
The `--file` option is used to configure client related data( see `lbc_conf.xml` for an example of the default client configuration file).

### Configuration File: lbc_conf.xml
The `lbc_conf.xml` is an XML file used to configure the LBC views.

    Format/Syntax:

    <client>
        <bucket>
            bc_id   = "<bucket id>"
            name    = "<bucket name>"
            color   = "<color>"
            label   = "<label>"
            icon    = "<icon>"
            tooltip = "<tooltip>"
        </bucket>
        <lightblock>
            lb_id   = "<light block id>"
            name    = "<light block name>"
            color   = "<color>"
            label   = "<label>"
            icon    = "<icon>"
            tooltip = "<tooltip>"
        </lightblock>
    </client>

Bucket, and Lightblock blocks are ordered based on their order in the file(i.e. order is preserved). 
Either a valid block `id` or `name` attribute must be present in each block. If both are used, the `name` attribute 
overrideds the `id` attribute. The `color` attribute in a given block is used to specify the color to use when 
rendering the corrosponding button in the LBC. If the `color` attribute is not specified, the button defaults 
to `white`. The `label` attribute defines the text to display on a given button unless the `icon` attribute is 
specified. The `icon` attribute overrides the `label` attribute.

Example `lbc_conf.xml` file:

    <client>
        <bucket name="201" color="red"  label="1"  icon="" tooltip="" />
        <bucket name="202" color="red"  label="2"  icon="" tooltip="" />
        <bucket name="203" color="red"  label="3"  icon="" tooltip="" />
        <bucket name="204" color="red"  label="4"  icon="" tooltip="" />
        <bucket name="205" color="red"  label="5"  icon="" tooltip="" />
        <bucket name="206" color="red"  label="6"  icon="" tooltip="" />
        <bucket name="207" color="red"  label="7"  icon="" tooltip="" />
        <bucket name="208" color="red"  label="8"  icon="" tooltip="" />
        <bucket name="209" color="red"  label="9"  icon="" tooltip="" />
        <bucket name="210" color="red"  label="10" icon="" tooltip="" />
        <lightblock  name="flame"    color="red"         label=""  icon="fire-icon.png"        tooltip="Flame"   />
        <lightblock  name="rainbow"  color="lime"        label=""  icon="rainbow-icon.png"     tooltip="Rainbow" />
        <lightblock  name="ocean"    color="dodgerblue"  label=""  icon="whale-ocean-icon.png" tooltip="Ocean"   />        
    </client>

To use a custom configuration file, something other than the defualt `lbc_conf.xml` file, the -f/--file option is required:

    $ python lbc.py -v -c -i <ip_address> -f <name_of_config_file>

    where <name_of_config_file> is the name of an alternate configuration file.
    For example iob2016_conf.xml or klingon_conf.xml.


### Generating a Configuration Stub
The generate switch (`-g`, `--generate`) parses the `conf.xml` file and generates a LBC compliant xml
for use in a custom LBC configuration file.

    $ python lbc.py -g
    $ python lbc.py --generate

    <client>
        <bucket name="201" color="red" label="1" icon="" tooltip="201" />
        <bucket name="202" color="red" label="2" icon="" tooltip="202" />
        ...
        <bucket name="250" color="blue" label="50" icon="" tooltip="250" />
        <lightblock name="flame"   color="lime"        label="1" icon="" tooltip="flame"   />
        <lightblock name="rainbow" color="green"       label="2" icon="" tooltip="rainbow" />
        ...
        <lightblock name="ocean"   color="deepskyblue" label="3" icon="" tooltip="ocean"   />
    </client>

More likely than not, you will probably need to prune the output of this switch to only those buckets and lightblocks
that are applicable to your use case.


### Creating Customized Themes
LBC supports the creation of customized themes(i.e. colors, labels and icons). Here's an example of a custom `klingon` theme
that uses a `new_theme_name`_conf.xml file and a set of theme specific icon images. The new theme related icon 
images should reside in `./static/images/new_theme_name` folder. So, for our `klingon` example, there's a `klingon_conf.xml` file
along with a set of icon images located at `./static/images/kilingon`

Links to our custom theme configuration file and the associated icons:
- [klingon_conf.xml](https://github.com/hooperfly/lightbucketcommander/blob/master/klingon_conf.xml)
- [klingon icons folder](https://github.com/hooperfly/lightbucketcommander/tree/master/static/images/klingon)

**Invocation & Screenshot:**

    $ python lbc.py -f klingon_conf.xml

![Alt Klingon Light Block View](doc/images/klingon_screen.png?raw=true "Klingon Light Block View")
    
### URL Parameters

#### Bucket Coloring Scheme
Each row of bucket buttons default to the colors specified for each block function, a column major view. 
This behavior can be overriden through the use of the `view_mode` URL parameter. If you would like to preserve/use
the colors assigned to each bucket for each row's color, set the `view_mode` URL paramater to `row`.

    localhost:5000/show/lightblock/?view_mode=row

Each row of bucket buttons will use the respective color assigned to each bucket in the `lbc_conf.xml` file, 
a row major view.

![Alt Light Block view_mode=row View](doc/images/lightblock_viewmode_screen.png?raw=true "Light Block view_mode=row View")

#### Resizing Buttons
The default button size is 64x64 pixels. Sometimes it is desireable to reduce or increase
button sizes based on display variants. The `button_size` URL parameter is used to specify a
desired button size. For example, to specify a button size of 40x40 pixels use the following:

    localhost:5000/show/lightblock/?button_size=40

![Alt Light Block buttonsize=40 View](doc/images/lightblock_buttonsize_screen.png?raw=true "Light Block buttonsize=40 View")

You can specify both `view_mode` and `button_size` URL parameters using the following sytnax:

    localhost:5000/show/lightblock/?view_mode=row&button_size=40


### Adding Client Data via Routes
If the `--file` option is not used when starting the LBC server, the client related configuration must
be completed using the `object`/client/add/`id` routes; where `object` is one of bucket or lightblock 
and `id` is a valid object id. The bucket and lightblock related `client` data 
need to be configured(see syntax below) prior to using one of the client views( `show/lightblock`).

    Syntax:

    - Bucket Route:       bucket/client/add/<ac_id>
    - Light Block Route: lightblock/client/add/<fb_id>
 
Example `bash` script that uses `curl` to configure client data for five buckets and three light blocks:

    #!/bin/bash
    host=127.0.0.1
    port=5000
    curl http://$host:$port/bucket/client/add/201
    curl http://$host:$port/bucket/client/add/202
    curl http://$host:$port/bucket/client/add/203
    curl http://$host:$port/bucket/client/add/204
    curl http://$host:$port/bucket/client/add/205
    curl http://$host:$port/lightblock/client/add/0
    curl http://$host:$port/lightblock/client/add/1
    curl http://$host:$port/lightblock/client/add/2


### Showing Client Views
Once the client related data is configured, the various client views of the LBC are available for use.

    Syntax:

    - Light Block Route: /show/lightblock/
    - Grid Route:        /show/grid/

Assuming the server is running on the local host(ip=127.0.0.1), type one of the following URL's into
a browser(e.g. Chrome, Firefox, etc...) to execute the respective client view. 

    localhost:5000/show/lightblock/
    localhost:5000/show/grid/

Of course, if you are using the IP address of your server system, the URL will use that IP address
in place of `localhost`. For example if the server were running on 192.168.16.12, the URL would
look like the following:

    192.168.16.12:5000/show/lightblock/
    192.168.16.12:5000/show/grid/

Remember to configure the bucket and lightblock client data prior to accessing 
the respective client view.

#### Light Block View
![Alt Light Block View](doc/images/lightblock_screen.png?raw=true "Light Block View")

#### Grid View
The `Grid` view is optimized to interact with a set of light buckets based on a given geometry. It provides a simple
interface for creating patterns using `pen` and `fill` modes.

![Alt Grid View](doc/images/grid_screen.png?raw=true "Grid View")

## Video Demos:
Here's an informal demo video of the Light Bucket Commander:

- [LBC: Light Block Video](https://youtu.be/XFHEub7xecc)

## TODO:
- [ ] Improve asynchronous request performance

## COMPLETED:
- [x] Updated grid view to reflect pen/brush state changes
- [x] Added lightblock_mode support for `grid` view
- [x] Added `-t/--test` command line argument and icons for `grid` view actions
- [x] Added first pass at a `grid` view
- [x] Seed the repo

