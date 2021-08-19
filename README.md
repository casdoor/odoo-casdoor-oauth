# odoo-casdoor-oauth
*Under construction... Feel free to raise issue if you find one!*  

This plugin utilizes Casdoor's OAuth function to log in Odoo for convenience.

View the [**Odoo module**](https://apps.odoo.com/apps/modules/14.0/casdoor_oauth/)

## Usage

1. You need to setup the Odoo instance on your host server, for this step, please reference the latest official Odoo setup [tutorial](https://www.odoo.com/documentation/14.0/developer/howtos/rdtraining/02_setup.html). **Make sure you can correctly setup the Odoo instance before proceeding to next step.**

2. Then you need to setup a Casdoor instance, for which you need to reference the latest official Casdoor setup [tutorial](https://github.com/casbin/casdoor). **Make sure you can correctly setup the Casdoor instance before proceeding to next step.**

3. Get this module by `git`:  

    ```shell
    $ git clone https://github.com/casdoor/odoo-casdoor-oauth.git
    ```
    or  
    get the [module](https://apps.odoo.com/apps/modules/14.0/casdoor_oauth/) on `Odoo App Store`.

4. Go to your Odoo instance `src` folder:  

   If your machine is Linux/UNIX, it should be in:  

    ```shell
    $ cd $HOME/src
    ```

    If there is not a `custom` folder, then make one and cd into the folder:

    ```shell
    $ mkdir custom
    $ cd custom
    ```

5. Place the cloned or downloaded (if you get it from Odoo App Store, you need to unzip the zip file to see the `casdoor_oauth` folder) `casdoor_oauth` folder here.  

6. Make sure you install all the dependencies:  

    ```shell
    $ cd casdoor_oauth
    $ pip install -r requirements.txt
    ```

7. Go back to the `odoo` folder:
    ```shell
    $ cd $HOME/src/odoo
    ```
    and run the following command

    ```shell
    $ ./odoo-bin --addons-path=../custom,addons -d rd-demo -u casdoor_oauth
    ```
    > Hint: `-d` means the database you want to use and `-u` means the module you want to update. Detailed usage and tutorial should be read [here](https://www.odoo.com/documentation/14.0/developer/howtos/rdtraining/04_basicmodel.html#object-relational-mapping).

8. If everything worked out so far, you should go to your running Odoo instance and go to its Apps page by clicking the top-left menu icon, select `Apps`  

    ![Apps](/casdoor_oauth/static/description/Apps.png)

    In the search box, cancel the `Apps` filter (because `casdoor_oauth` is a `Tool`).

    Then search for `casdoor_oauth`, it should pop up!

    ![search result](/casdoor_oauth/static/description/casdoor_oauth.png)

    Click `install`.  

9. After the install finished, redo `Step 7` above.

10. Now go to the top-left menu and click `Settings`, and you should be able to see the `Casdoor OAuth` tab in the left pane.


    ![Settings Screenshot](/casdoor_oauth/static/description/settings.png)

    Fill in the `Casdoor Authentication URL` in this format (replace the `YOUR.SERVER.URL` with your own Casdoor instance's URL):
    ```shell
    YOUR.SERVER.URL/login/oauth/authorize
    ```
11. 
    Then go to your Casdoor instance, click the `Applications` tab on the top navbar.

    ![casdoor applications](/casdoor_oauth/static/description/casdoor_app.png)

    Select your specified application and find the `Client ID` and `Client secret` in the settings page.

    Below the two fields, there is a field called `Redirect URLs`, make sure you fill it in this format (replace the `YOUR.ODOO.INSTANCE.URL` with your Odoo instance's URL):
    ```shell
    YOUR.ODOO.INSTANCE.URL/auth_oauth/signin
    ```

    ![id and secret](/casdoor_oauth/static/description/id_secret_url.png)    

    You should copy these two info and go back to the Odoo setting page and paste them into your `Casdoor Client ID` and `Casdoor Client Secret` fields, respectively.

    Then make sure the `Active` checkbox is selected.

    **Remember to click the `Save` button on the top left corner before you leave the page!** 

11. By now everything is good to go! Try log out your current user and on the login page you should be able to see the option `Log in with Casdoor`:

    ![Login Screenshot](/casdoor_oauth/static/description/login_page_screenshot.png)

    Click on it and log into Odoo using Casdoor!
