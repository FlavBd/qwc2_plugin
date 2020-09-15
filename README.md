The QWC2 plugin allows to publish and update QGIS projects on the web from QGIS desktop.

The plugin has an associated server component that lives in the QWC2 microservices ecosystem.

Below is a blueprint of the architecture .

![From the user to the application](img_plugin/plugin_archi.png)

There are two prerequisite :

* To open the plugin window and add a new project in the application, it is necessary to have **a QGIS (.qgs) project opened in QGIS Desktop**. Once the window is opened the user can also configure projects that are already published. If the user only want to modify an existing project, he must open it in QGIS Desktop to open the QWC2 plugin configuration window.

* The user also needs to know the url of the server, his/her username and password.

To a better understanding of what we realised, we propose here [a short video of the plugin](https://youtu.be/XK5nevc4D9g) : 

Like you can see, the first step is to create and configure your project in QGIS Desktop : symbology, QGIS Server services.
After you click on the button an interface opened where the user gives the url server, username and password. Clicking on "test connection" allows the connection to the server and add information about projects already in the app and the project you want to add in the interface. You can modify informaiton and then click to add the project in the application. After some minutes, the project is in the app! If you refresh your web page you can see the project and the symbology you choose.

# To test the plugin... how it works now

Clone this repository in the QGIS plugin folder: 

```
git clone <this repository> ~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/qwc2_plugin
```

Run the server component locally:
```sh
cd  ~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/qwc2_plugin
virtualenv -p python3 venv
. venv/bin/activate
pip install flask
python server.py
```

It is necessary to have a `themesConfig.json` in the path defined in `server.py`, by default `tmp/themesConfig.json`.

Open QGIS desktop, create a QGIS project, configure QGIS server services (WMS, WFS...), activate the plugin and click on the QWC2 icon in the plugin toolbar (the third one) ![](img_plugin/icon.png)

The configuration dialog opens:

![](img_plugin/dialog.png)

It is divided in two part:

* in the authentication part, the user complete the required information to connect to the server. The user click on *test connection* to check url and credentials and get the current configuration.
* in the project part updated information from the `themesconfig.json` are presented. The default diplayed project is the one currently opened in QGIS. The user can display/configure all projects already on the server: scales, background, default background and searchproviders. When the user click on **ok** information sent to the server component that saves in `themesConfig.json`.

We created a micro service with Flask to :
* check if the user informations are correct and tranfert QGIS project already in QWC2 application in the plugin interface on QGIS,
* transfert the new information of the projects choosen by the user and rebuild the app

Also, thanks to `server.py` if th zip file of the `plugin` directory is install on your server, you can upload it by adding `/qgis/plugin` at the end of your server url. A zip file is porposed to the user who can activate it with the QGIS Plugin Manager.

# Way to improve it... how it will work

Some improvements that we can think of after that:
* control if the project has QGIS Server services activated,
* transfer layers symbols to the server (e.g. in case of custom svg symbols)
* transfer datasources (shapefiles, geopackages) to the server if the data used by the project are not already available "online" (note: the server typically hosts a PostGIS server)

# Talk about it ...

We already talk about this plugin in [the mailling list QWC2](http://osgeo-org.1560.x6.nabble.com/New-features-in-QWC2-td5434695.html) and in [an issue on github](https://github.com/qgis/qwc2-demo-app/issues/3). 

Feel free to add comments or/and suggest changes.
