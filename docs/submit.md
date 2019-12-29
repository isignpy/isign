
# Submitting a resigned app to Apple

Unfortunately, when using isign, you will not be able to simply let XCode figure out signing and submitting for you.

Here are some possible procedures for doing this. They worked as of December 2019 with current MacOS and the
Apple Developer ecosystem.

## Manual procedure

We assume you are using the `bash` shell on a contemporary MacOS computer.

The overview: we will resign the app locally, and then upload it to App Store Connect via `xcrun altool`.

### Preparation (one-time only)

Add your Apple Developer Account App Store username as an environment variable to your `.bash_profile`. 
In most cases, this is identical to your Apple Developer Account username, and is usually an email address.

```bash
export APP_STORE_USERNAME=you@your.domain
```

You might also want to add this to your `.bash_profile`, to set up paths to additional tools such as `altool`.
 
```bash
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
  ```bash
  $ export APP_STORE_PASSWORD=$(lpass show developer.apple.com-altool --password)
  ```
  

In the following examples, we'll assume that (somehow) the password exists in the environment variable 
`$APP_STORE_PASSWORD`.





### When you build your app

Open your app project in XCode.


#### Set up identifier on the App Store

You need to prepare the app store to receive an app with this identifier.

In XCode, get the Bundle Identifier by clicking on the top node of the project, and in the
editor pane, navigating to the "General" tab.

Your Bundle Identifier will look something like `com.example.yourAppName`.

Next, switch to a web browser. Log into [App Store Connect](https://appstoreconnect.apple.com/)

Click "My Apps".

Click the "+" symbol to add an app.

Select a "New App"

In the next form, fill it out as you please, but make sure to select:

* Platforms: iOS

* Bundle ID: Choose options that get you a Bundle ID as above, `com.example.yourAppName`.

  You may end up choosing a combination of wildcard and suffix, such as
  * `*` + `com.example.yourAppName` = `com.example.yourAppName`
  * `com.example.*` + `yourAppName` = `com.example.yourAppName`

#### Set up a distribution provisioning profile for this app.

Your mileage may vary here, but sometimes the App Store does not like to use wildcard
application identifiers. So, you will need to create a provisioning profile that
matches the application identifier above, exactly.

In a web browser, go to developer.apple.com > Certificates, Identifiers and Profiles.

Register a new provisioning profile.

Select Distribution > App Store

Select the Application ID you just created above.

Select Certificate to Include. (Note, you should have that certificate already in PEM form...)

Download the new provisioning profile. You may get the option to install it into XCode (which of course you can do)
but also make sure to download it to a location where you can use it in an isign command-line argument. For example:

`isign -k yourKey.pem -c cert.pem -p <the provisioning profile you just downloaded...> yourApp.ipa`

However, when doing doing app distribution, I like to use `isign`'s -n feature to point to a directory with the
following well-known structure of `key.pem`, `certificate.pem`, and `isign.mobileprovision`.

Here, I have a single directory with my usual key and certificate, which are symlinked in. And the specific
provisioning profile for this app is availabvle in this directory as a regular file, renamed to `isign.mobileprovision`.

```
$ ls -la ~/.isign-distribution-isignTestApp/
total 16
drwxr-xr-x    5 neilk  staff   160 Dec 29 14:30 .
drwxr-xr-x+ 236 neilk  staff  7552 Dec 29 14:39 ..
lrwxr-xr-x    1 neilk  staff    38 Dec 29 14:29 certificate.pem -> ../.isign-distribution/certificate.pem
-rw-r--r--@   1 neilk  staff  7343 Dec 29 14:30 isign.mobileprovision
lrwxr-xr-x    1 neilk  staff    30 Dec 29 14:29 key.pem -> ../.isign-distribution/key.pem
```

Then I can do a simple command line resign, like this:

```
isign \
    -n ~/.isign-distribution-isignTestApp \
    -o resigned/isignTestApp.ipa
    isignTestApp.ipa
```

#### Test this

You may now wish to test this by signing and uploading an app directly from XCode.

Archive the project, choose to "Distribute" the app, and then choose "App Store Connect" and
automatically manage signing.




#### Create the IPA to be resigned

At the top of the window select “Generic iOS Device” as your build target.
 
Select “Product > Archive”.

This will compile your project, then pop up the Archives window.

Select the archive you just made and press the “Distribute App” button.

Select “App Store Connect”, and press “Next”.

Select “Export”,  and press “Next”.

Select the appropriate options for bitcode and symbol retention, and press  “Next”.

Select “Automatically manage signing”. (We're going to let XCode sign it once for us, with some developer identity,
and resign it later with `isign`.)

XCode will present you with a summary of all these options. Confirm them by pressing “Export” and select a 
destination directory.

In the terminal, cd to the directory you created, there should be an IPA there.



#### Resign and submit to Apple

When you submit to Apple, you need to keep bumping the bundle version. If you don't have some automatic
way to do that, you can manually edit the file `Info.plist` or use `isign`'s `-i` option to edit the
`CFBundleVersion` while resigning.

```bash
isign \
    -n ~/.isign-distribution-isignTestApp \
    -i CFBundleVersion=2 \
    -o basic-resigned-dist/isignTestApp.ipa \
    basic-dev/isignTestApp.ipa
```

Use `isign` to resign this IPA, for example

Lastly (and this is what we've been building up to...) use `altool` to validate and submit:

```bash
$ xcrun altool --validate-app --file ./resigned.ipa --username "$APP_STORE_USERNAME" --password "$APP_STORE_PASSWORD"
$ xcrun altool --upload-app --file ./resigned.ipa --username "$APP_STORE_USERNAME" --password "$APP_STORE_PASSWORD"

```



## Submitting a resigned app without source available

This is for the unlikely case where you have an IPA, and want to resign it to for App Store Distribution with a completely different organization.

First, be aware that if you try to distribute a resigned version of someone else's work without their permission, you are a) a bad person b) going to be in trouble. They have ways of catching you.

In the event that you do have permission, or, if you simply want to do some testing of isign, here's how you would do it.

You have to override the existing bundle identifier, from say `test.originalapp` to `com.example.myapp` this is what you need to do.

Each app has a bundle identifier, like `com.example.mytestapp`.  You must:
* Create an application record in App Store Connect.
* Create an identifier matching this bundle
* Create a certificate compatible with the iOS App Store for this identifier
* Create a provisioning profile compatible with the iOS App Store and this bundle identifier.
* when resigning, use the `-i` option to change the bundle when resigning, e.g.

`isign -i CFBundleIdentifier=net.neilk.mytestapp -o resignedWithNewCFBI.ipa original.ipa`

Many apps can be resigned with only the CFBundleIdentifier changed, but not all. For instance,
apps that are part of an app group will need other properties edited.

TBD: add docs for such properties here.


## Troubleshooting

### Errors with altool validate-app

* Invalid Provisioning Profile: Maybe you're submitting an app resigned with a development key or development
  provisioning profile. You need to resign the app with a distribution key and provisioning profile.

* Entitlements: Note that isign uses the entitlements that are embedded in your provisioning profile. You have
  two options to fix this: generate a new provisioning profile at Developer.apple.com, or, create your own
  alternate entitlements file and use isign's command-line arguments to insert it.


