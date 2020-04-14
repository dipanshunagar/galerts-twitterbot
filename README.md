# A Google Alerts based TwitterBot
A twitter bot backend to fetch URLs from google alerts and push them out as tweets with zero infra cost.

## How to use:
1. Set up your google alert with the `Deliver to` field as `RSS Feed`. If this field is disabled, [try this:](https://support.google.com/websearch/forum/AAAAgtjJeM4oNR25UbTOL8/?hl=en) while you are on the Google Alerts page, you will have the Settings (Gear) icon in the My alerts section. Please click on that and uncheck the option Digest and then click on Save. 

    Remember to copy the RSS Feed URL once the GAlert is saved, using the RSS icon in the list of you set alerts.

2. Sign up for twitter dev account, create an application and enter the api connection credentials in main.py

3. Set up a heroku application and push these files into it.

4. Visit `<your app name>.herokuapp.com/news/autotweet` (without a trailing slash) in a browser to test. It should give a JSON response with a status and tweet count.

5. Now we need to call this endpoint in regular intervals. Go to script.google.com, create a new project. Enter the following code and plug in your heroku app URL:
```
function tweetbot_timer() {
  Logger.log(UrlFetchApp.fetch("https://<your app name>.herokuapp.com/news/autotweet"));
}
```

6. Set up a new trigger for this script as per your preference, and you're done.
