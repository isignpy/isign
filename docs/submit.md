
# Submitting a resigned app to Apple

`isign` offers a lot of flexibility in signing. Unfortunately, it can be difficult to sign an app correctly such that the App Store will accept a submission. In 2020, XCode figures out a lot of this for you, but you'll have to do it manually here.

Here are some possible procedures for doing this. They worked as of February 2020 with current MacOS and the
Apple Developer ecosystem.

## Procedure

We assume you are using the `bash` shell on a contemporary MacOS or Linux computer, and that you have access to 

The plan is to adjust properties of the app as required, and then upload it to App Store Connect via `xcrun altool`.

### Preparation (one-time only)

Add your Apple Developer Account App Store username as an environment variable to your `.bash_profile`. 
In most cases, this is identical to your Apple Developer Account username, and is usually an email address.

```shell script
export APP_STORE_USERNAME=you@your.domain
```

You might also want to add this to your `.bash_profile`, to set up paths to additional tools such as `altool`.
 
```shell script
xcode-select -r     # to set up paths. 
```

Once added, restart your terminal to get the correct paths.

With your web browser, on `https://developer.apple.com/`, prepare your accounts and certificates for distribution.

We'll also need to set up an "app password" to be used by `altool`. Log in to `https://appleid.apple.com/`, and
scroll to the "Security" section. Set up an app password, and label it "altool". Store this password somewhere 
secure. 

### Password security

Later on you're going to need to use this password on the command line. _This is a potential 
security vulnerability_. The command and its arguments can be observed by other processes on your machine, and it will automatically be stored in your `.bash_history`.

So, the best practice would be to store it someplace secure, and then obtain it for use on the command line, in some way that doesn't leave traces.

Here are a couple of options:

* Apple Keychain: If you choose to store the above password in the Apple Keychain, there is a way to use it directly
  with the command line for `altool` where you would normally use a password. See `man altool` for the details.
  
* Other password managers: you can simply cut & paste from your password manager app such as 1Password or Lastpass.
  
  Since you probably want to create builds very often, you can also try automating this with a command-line tool to 
  retrieve secrets from your password manager. 
    * [1Password command-line tool](https://1password.com/downloads/command-line/), or `brew install 1password-cli`
    * [Lastpass command-line tool](https://support.logmeininc.com/lastpass/help/use-the-lastpass-command-line-application-lp040011) or `brew install lastpass-cli`
  
  For example, here's how one might use the LastPass `lastpass-cli` package.
  
  In your LastPass vault, make a pseudo-website called "developer.apple.com-altool" 
  without a username and using the altool password as password. Then you can make a bash script 
  like this:
  ```shell script
  $ export APP_STORE_PASSWORD=$(lpass show developer.apple.com-altool --password)
  ```
  

In the following examples, we'll assume that (somehow) the password exists in the environment variable 
`$APP_STORE_PASSWORD`.

### When you build your app

Open your app project in XCode.


#### Set up apps on the App Store

If you have already been uploading apps to the App Store, you may already have all these things set up. However, occasionally, XCode creates records that you cannot view in the App Store Connect portal, so you may need to do it again.

#### Overview

Ultimately, you're trying to get one or more provisioning profiles and then you'll hand those to `isign` to complete your signing. Unfortunately, we have to get into the nitty-gritty of how this all works to get the right provisioning profiles.

The basic unit of software on MacOS, iOS and WatchOS is the _Bundle_. A simple app is just a bundle. Each app has at least one *Bundle Identifier*, that will look something like `com.example.myapp`.

Some apps have more than one bundle. For instance, if you're including a Watch app, these days
this implies an embedded WatchOS app. You may also have one or more App Extensions ("Appex"). These will have bundle ids like `com.example.yourAppName.watchkitapp`
and `com.example.yourAppName.watchkitapp.watchkitextension`.

Apple has a related concept called an *Application Identifier*. In many cases this is identical to your bundle id, but an application identifier can use wildcards, like `com.example.yourAppName.*`. This is handy when you want to define a provisioning profile that covers all of the bundles in your app.

When you want to sign the app, you're going to get a provisioning profile that identifies your organization plus that application identifier. This is just your Apple "Organizational Unit" (sometimes called the Team ID) plus the bundle id. Apple Team IDs are usually written in all caps, so it might look something like `TEAMID.com.example.myapp.*`. 

Note you can cover all of those bundles with one provisioning profile if your provisioning profile is signed with a "wildcard" id like `TEAMID.com.example.yourAppName.*`. However, for distribution, some organizations like to use fully qualified bundle ids for every bundle. If that's the case for you, then you'll need a provisioning profile for every bundle.

The ultimate goal is to obtain provisioning profile(s) that cover all the bundles included in your app. A provisioning profile contains a lot of things, but you can think of it as Apple's express signed permission about what you can do with an app. These will be embedded in your app and will tell the phone it's okay for the app to do what it does.

In essence, a provisioning profile tells the phone that
- Your organization... (Team Identifier)
- ...should be able to publish this iOS app / appex / watchOS app , etc... (Bundle Ids) 
- ...that can do these things... (Entitlements and Capabilities)
- ...on these phones. (a manually specified list of phones, your whole organization, or for Apple to release to the world) 

Once you have the necessary provisioning profile(s), you'll pass them to `isign` and it will handle the rest.

#### Get the identifiers you need

In XCode, get the Bundle Identifier(s) by clicking on the top node of the project, and in the
editor pane, navigating to the "General" tab.

Your Bundle Identifier will be displayed in the pane of information, and will look something like `com.example.yourAppName`.

If you have other bundles within your app, and you are not going to use a provisioning profile with a wildcard that covers them all, you'll need to get more bundle ids. There will be a pair of chevrons to the left of "General" tab. Click on that to switch to the other bundles, and read their bundle id from the information pane.

#### Preparing the App Store for these bundles/apps

You now have your app's main executable bundle id, and potentially a few others, for WatchOS apps or other extensions.

Next, switch to a web browser. Log into [App Store Connect](https://appstoreconnect.apple.com/).

Click "My Apps".

Use the "+" icon to create a new iOS app for the main bundle in your app. Use the bundle identifier for the main app that you retrieved above.

#### Register identifiers

In a web browser, go to developer.apple.com > Certificates, Identifiers and Profiles. Examine what identifiers you already have and if you're going to want to make any more.

* Bundle ID: Choose options that get you a Bundle ID as above, `com.example.yourAppName`.

Click on Identifiers and use the '+' button to make a new one.

Register an identifier with your Bundle Identifier as above. Select iOS. Give the app the necessary capabilities.

If necessary, register more identifiers (as when signing each bundle in your app with its own provisioning profile).

#### Test this

You may now wish to test this by signing and uploading an app directly from XCode.

Archive the project, choose to "Distribute" the app, and then choose "App Store Connect" and automatically manage signing.


#### Obtain provisioning profile(s)

You will need to create (or download) at least one provisioning profile.

In a web browser, go to developer.apple.com > Certificates, Identifiers and Profiles.

If you do not see a provisioning profile defined that fits your use cases, click on Provisioning Profiles and use the '+' button to make a new one.

Select Distribution > App Store. Press Continue

Select the Application ID you just created above.

Select Certificate to Include. (Note, you should have that certificate already in PEM form...)

Download the new provisioning profile. You may get the option to install it into XCode (which of course you can do)
but also make sure to download it to a location where you can use it in an isign command-line argument. 

It does not matter what the name of the provisioning profile is.

Repeat this process for every provisioning profile that you have determined you will need.

You may find it convenient to store all the files in one directory, like this. 

```shell script
$ ls -l creds-myApp
total 192
-rw-r--r--    1 neilk  staff  2452 Nov 17 17:09 certificate.pem
-rw-------    1 neilk  staff  1905 Nov 17 17:09 key.pem
-rw-r--r--@ 1 neilk  staff   7348 Jan 15 09:57 myApp.mobileprovision
```

But for complex apps with sub-bundles signed with fully qualified application ids, you'll have more than one provisioning profile, in the same directory. The names of the `.mobileprovision` files do not matter, but this is how Apple will typically name them.


```shell script
$ ls -l creds-myApp
total 192
-rw-r--r--    1 neilk  staff  2452 Nov 17 17:09 certificate.pem
-rw-------    1 neilk  staff  1905 Nov 17 17:09 key.pem
-rw-r--r--@ 1 neilk  staff   7348 Jan 15 09:57 myApp.mobileprovision
-rw-r--r--@ 1 neilk  staff   7421 Jan 22 11:33 myAppWatchkitappWatchkitextension.mobileprovision
-rw-r--r--@ 1 neilk  staff   7382 Jan 22 11:33 myAppWatchkitappdistribution.mobileprovision
```

#### Create the IPA to be resigned

We're now going to create an IPA that is signed with some non-distribution credentials and resign them, using isign, to have distribution credentials.

At the top of the window select “Generic iOS Device” as your build target.
 
Select “Product > Archive”.

This will compile your project, then pop up the Archives window.

Select the archive you just made and press the “Distribute App” button.

Select “App Store Connect”, and press “Next”.

Select “Export”,  and press “Next”.

Select the appropriate options for bitcode and symbol retention, and press  “Next”.

Select “Automatically manage signing”. (We're going to let XCode sign it once for us, with some developer identity, and resign it later with `isign`.)

XCode will present you with a summary of all these options. Confirm them by pressing “Export” and select a 
destination directory.

In the terminal, cd to the directory you created, there should be an IPA there.


#### Resign and submit to Apple

Then you can do a simple command line resign, like this:

```
isign \
    -n ~/creds-myApp \
    -o resigned.ipa
    isignTestApp.ipa
```

Lastly (and this is what we've been building up to...) you use `altool` to validate and submit:

```shell *script*
$ xcrun altool --validate-app --file ./resigned.ipa --username "$APP_STORE_USERNAME" --password "$APP_STORE_PASSWORD"
$ xcrun altool --upload-app --file ./resigned.ipa --username "$APP_STORE_USERNAME" --password "$APP_STORE_PASSWORD"

```

For your convenience, you can also try using the `bin/submit.sh` script in this package, which does the same thing as the above two lines of shell, but a bit more conveniently.

Note: when you submit to Apple, you need to keep bumping the bundle version. If you don't have some automatic way to do that, you can manually edit the file `Info.plist` or use `isign`'s `-i` option to edit the `CFBundleVersion` while resigning.


## Submitting a resigned app without source available

This is for the unlikely case where you have an IPA, and want to resign 
it to for App Store Distribution with a completely different 
organization. For instance, perhaps you have an IPA compiled with an 
old version of XCode that you want to keep testing. Or, you may be 
running a test lab that runs tests on real devices, and you want to 
accept IPAs from other teams or organizations.

You have to override the existing bundle identifier, from say 
`test.originalapp` to `com.example.myapp` this is what you need to do.

Each app has a bundle identifier, like `com.example.mytestapp`.  You must:
* Create an application record in App Store Connect.
* Create an identifier matching this bundle
* Create a certificate compatible with the iOS App Store for this identifier
* Create a provisioning profile compatible with the iOS App Store and this bundle identifier.
* when resigning, use the `-i` option to change the bundle when resigning, e.g.

`isign -i CFBundleIdentifier=net.neilk.mytestapp -o resignedWithNewCFBI.ipa original.ipa`

Many apps can be resigned with only the CFBundleIdentifier changed, but not all. For instance, apps that are part of an app group will need other properties edited.

## Troubleshooting

### Errors with altool validate-app

* Invalid Provisioning Profile: Maybe you're submitting an app resigned with a development key or development
  provisioning profile. You need to resign the app with a distribution key and provisioning profile.

* Entitlements: Note that isign uses the entitlements that are embedded in your provisioning profile. You have
  two options to fix this: generate a new provisioning profile at Developer.apple.com, or, create your own
  alternate entitlements file and use isign's command-line arguments to insert it.
