
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

<<<<<<< HEAD
Next, switch to a web browser. Log into [App Store Connect](https://appstoreconnect.apple.com/)

Click "My Apps".
=======
!! you have to create separate identifiers AND provisioning profiles for watchkit apps
!! how are we gonna tell isign to do this
>>>>>>> wip

bundle versions must all match!
in this case, isign does the right thing already


#### Create an identifier

In a web browser, go to developer.apple.com > Certificates, Identifiers and Profiles.

* Bundle ID: Choose options that get you a Bundle ID as above, `com.example.yourAppName`.

Click on Identifiers and use the '+' button to make a new one.

Register an identifier with your Bundle Identifier as above. Select iOS. Give the app the necessary
capabilities.

#### Set up a distribution provisioning profile for this app.

Caveat - the following advice may be incorrect; at present all we have is folklore.

Your mileage may vary here, but sometimes the App Store does not like to use wildcard app identifiers,
e.g. `YOURTEAMID.net.neilk.*`

So, you will need to create a provisioning profile that
matches the application identifier above, exactly.

In a web browser, go to developer.apple.com > Certificates, Identifiers and Profiles.

Click on Provisioning Profiles and use the '+' button to make a new one.

Select Distribution > App Store. Press Continue

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

* altool validates and submits your app correctly, but you get an email from Apple later complaining about:
  * ITMS-90034: Missing or invalid signature: The bundle 'com.example.yourApp' at bundle path
    'Payload/yourApp.app' is not signed using an Apple submission certificate. (WORKING ON IT!!!)




### Notes on WatchKit

1) invalid entitlements

"Error Domain=ITunesConnectionOperationErrorDomain Code=1091
 \"Invalid Code Signing Entitlements. 
 Your application bundle's signature contains code signing entitlements that are not supported on iOS. 
 Specifically, value 'L37S4Z6BE9.net.neilk.isignTestWatchApp'  for key 'application-identifier' in 
 'Payload/isignTestWatchApp.app/Watch/isignTestWatchApp WatchKit App.app/isignTestWatchApp WatchKit App' 
 is not supported. This value should be a string starting with your TEAMID, 
 followed by a dot '.', followed by the bundle identifier.\" 
 UserInfo={NSLocalizedRecoverySuggestion=Invalid Code Signing Entitlements. 
 
"Error Domain=ITunesConnectionOperationErrorDomain Code=1091 
\"Invalid Code Signing Entitlements. 
Your application bundle's signature contains code signing entitlements that are not supported on iOS. 
Specifically, value 'L37S4Z6BE9.net.neilk.isignTestWatchApp' for key 'application-identifier' in 
'Payload/isignTestWatchApp.app/Watch/isignTestWatchApp WatchKit App.app/PlugIns/isignTestWatchApp WatchKit Extension.appex/isignTestWatchApp WatchKit Extension' 
is not supported. This value should be a string starting with your TEAMID, 
followed by a dot '.', followed by the bundle identifier.\" 
UserInfo={NSLocalizedRecoverySuggestion=Invalid Code Signing Entitlements. 


Note: looking at opendiff of the asn1parsed provisioning profiles
1)
?? for watchkit app it looks like XCode selected "SimulatedCustomerApp" which has wildcard certs
will this work for submitting to the app store?
passed validation and submission and App Store.

xcode using auto-management, in provisioning profile...
<key>DeveloperCertificates</key>
	<array>
		<data>MIIFpzCCBI+gAwIBAgIIbKb6q5aydEcwDQYJKoZIhvcNAQELBQAwgZYxCzAJBgNVBAYTAlVTMRMwEQYDVQQKDApBcHBsZSBJbmMuMSwwKgYDVQQLDCNBcHBsZSBXb3JsZHdpZGUgRGV2ZWxvcGVyIFJlbGF0aW9uczFEMEIGA1UEAww7QXBwbGUgV29ybGR3aWRlIERldmVsb3BlciBSZWxhdGlvbnMgQ2VydGlmaWNhdGlvbiBBdXRob3JpdHkwHhcNMTkwODEyMDExNTQxWhcNMjAwODExMDExNTQxWjCBmjEaMBgGCgmSJomT8ixkAQEMCkwzN1M0WjZCRTkxPTA7BgNVBAMMNGlQaG9uZSBEaXN0cmlidXRpb246IE5laWwgS2FuZGFsZ2FvbmthciAoTDM3UzRaNkJFOSkxEzARBgNVBAsMCkwzN1M0WjZCRTkxGzAZBgNVBAoMEk5laWwgS2FuZGFsZ2FvbmthcjELMAkGA1UEBhMCVVMwggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQCegTSJUQqD8NyGPLwadZNXQXe5nsey+7qQYOU/v1Wsn3g+MlNulhFUtOfuBCAiwbHmN16qUkws2AtCRB7+8asXuhp/edoRdKOLOrfJTjV8Xhmch3lCuuszk7FVlDx/+KHChv/j8Ozjp/DxXgsaGeitiYsGPEZh1DNVUxON7/k1rJy0vZcjeJpHkfCHM1L0QXgbzj7N5f5bn8dJ6Mw6RncK05q092l/LyHK4gkWTFF3/jCASFJbTqwFaWkxTx6lGdZ7xdD5Jp/s1IPik2Mk9Tel3L1c2nwfWX3z4EiW9eM+Akp78KEHXLUt82c7Fd2E2A+lw2GwH+t6cU/4W1PqLCUlAgMBAAGjggHxMIIB7TAMBgNVHRMBAf8EAjAAMB8GA1UdIwQYMBaAFIgnFwmpthhgi+zruvZHWcVSVKO3MD8GCCsGAQUFBwEBBDMwMTAvBggrBgEFBQcwAYYjaHR0cDovL29jc3AuYXBwbGUuY29tL29jc3AwMy13d2RyMTEwggEdBgNVHSAEggEUMIIBEDCCAQwGCSqGSIb3Y2QFATCB/jCBwwYIKwYBBQUHAgIwgbYMgbNSZWxpYW5jZSBvbiB0aGlzIGNlcnRpZmljYXRlIGJ5IGFueSBwYXJ0eSBhc3N1bWVzIGFjY2VwdGFuY2Ugb2YgdGhlIHRoZW4gYXBwbGljYWJsZSBzdGFuZGFyZCB0ZXJtcyBhbmQgY29uZGl0aW9ucyBvZiB1c2UsIGNlcnRpZmljYXRlIHBvbGljeSBhbmQgY2VydGlmaWNhdGlvbiBwcmFjdGljZSBzdGF0ZW1lbnRzLjA2BggrBgEFBQcCARYqaHR0cDovL3d3dy5hcHBsZS5jb20vY2VydGlmaWNhdGVhdXRob3JpdHkvMBYGA1UdJQEB/wQMMAoGCCsGAQUFBwMDMB0GA1UdDgQWBBQfEBI9Kiq+odNZ+xBgHVTpyggwLjAOBgNVHQ8BAf8EBAMCB4AwEwYKKoZIhvdjZAYBBAEB/wQCBQAwDQYJKoZIhvcNAQELBQADggEBAEEJJXRXn61QdzIzDVf83CKrTKUfEXN/ixHzkQ29fQYgwuVqNYg+r2ykYlQx+3Txuu0r4F1PF+qQfMBq3D8Sq14N43amV/NvIgd4BFJfvTQrGYrjnMBk7ELDpU/J66YwnDt4wTKexL8eLD4jfPNSYpyCf+kryTRfoE5hXKpEn2jrgNbUSPGyauvv6w1GmgNgYmxB+fWF6Xqsy5aWKZ0wCpNd262RGDh3dPEtqtseSwYrzxlqiZRTXR2htU6prIr3sfoC2uOXtHiV1yN1e5XfRk4iSWybu/ZAJHncignhMCDZS8d225SCBUppfXktH7McuJH6bDaiy+7Y6cm8D5JRVUw=</data>
		<data>MIIFuzCCBKOgAwIBAgIIGUbgCb5Lq+8wDQYJKoZIhvcNAQELBQAwgZYxCzAJBgNVBAYTAlVTMRMwEQYDVQQKDApBcHBsZSBJbmMuMSwwKgYDVQQLDCNBcHBsZSBXb3JsZHdpZGUgRGV2ZWxvcGVyIFJlbGF0aW9uczFEMEIGA1UEAww7QXBwbGUgV29ybGR3aWRlIERldmVsb3BlciBSZWxhdGlvbnMgQ2VydGlmaWNhdGlvbiBBdXRob3JpdHkwHhcNMTkwOTI5MTkzMzIzWhcNMjAwOTI4MTkzMzIzWjCBmTEaMBgGCgmSJomT8ixkAQEMCkwzN1M0WjZCRTkxPDA6BgNVBAMMM0FwcGxlIERpc3RyaWJ1dGlvbjogTmVpbCBLYW5kYWxnYW9ua2FyIChMMzdTNFo2QkU5KTETMBEGA1UECwwKTDM3UzRaNkJFOTEbMBkGA1UECgwSTmVpbCBLYW5kYWxnYW9ua2FyMQswCQYDVQQGEwJVUzCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBAOF8e0GnMnPaJCRzg9c6MOjm99ikbHScCIJBcoyXWkH3PkiRrDy106/gjeLDOtG6psbjKl++TGek+7pP85RKwbHn9vCfu3pqcHe+HZ/LNL2puft4VMObuTHvROkpOSMpoxLZd6iyy+9hADSvhZ+8jaAXe+t3Fz3xicbb+IfA729B32Ly6INDsAfrXHXWPM6uVnpvBd66QGuMFUom+u3b0z7+6Ze5zrkqwsDD0lbokACXyP/OWUoAfpzX5ji8QxxEWfzy0UO5VuNysg7mL/ijK+miDo5XzNglD/xSCo2smF7M7OlO4grMv867jmB9H9r60HRneaWqW/m1gd1nXdJT9G0CAwEAAaOCAgYwggICMAwGA1UdEwEB/wQCMAAwHwYDVR0jBBgwFoAUiCcXCam2GGCL7Ou69kdZxVJUo7cwPwYIKwYBBQUHAQEEMzAxMC8GCCsGAQUFBzABhiNodHRwOi8vb2NzcC5hcHBsZS5jb20vb2NzcDAzLXd3ZHIyMDCCAR0GA1UdIASCARQwggEQMIIBDAYJKoZIhvdjZAUBMIH+MIHDBggrBgEFBQcCAjCBtgyBs1JlbGlhbmNlIG9uIHRoaXMgY2VydGlmaWNhdGUgYnkgYW55IHBhcnR5IGFzc3VtZXMgYWNjZXB0YW5jZSBvZiB0aGUgdGhlbiBhcHBsaWNhYmxlIHN0YW5kYXJkIHRlcm1zIGFuZCBjb25kaXRpb25zIG9mIHVzZSwgY2VydGlmaWNhdGUgcG9saWN5IGFuZCBjZXJ0aWZpY2F0aW9uIHByYWN0aWNlIHN0YXRlbWVudHMuMDYGCCsGAQUFBwIBFipodHRwOi8vd3d3LmFwcGxlLmNvbS9jZXJ0aWZpY2F0ZWF1dGhvcml0eS8wFgYDVR0lAQH/BAwwCgYIKwYBBQUHAwMwHQYDVR0OBBYEFID3YsUR7Hv85KrH+OwrG+tCfjrGMA4GA1UdDwEB/wQEAwIHgDATBgoqhkiG92NkBgEHAQH/BAIFADATBgoqhkiG92NkBgEEAQH/BAIFADANBgkqhkiG9w0BAQsFAAOCAQEAu9o1ms4/A9k5uqhbZRHQoqWXY3n+IbbNKKwUe20mhOvw1zdEGG4YhDmcMR0Mz+e+uRPBpc59SXVZMjcD9tiBQsJS4KHXBpaZVx5B7ERSJQNhIH43hvZnZFddFQyN4hA/9c0TTC92ejIdoGDafEA79fYaYPedGxd6Fkp+LEa9uZvnhPN84xGOO1TV+ozKq1Nz1LJaxYLxu57Ux+fNdL/RJMWw0ZB5wXDdYZNW1qMeIZoNXt/Nz6pA9qhiS0dUs46B2mxms1YdQLsGhqE6PZQEoRJChxZRczoK3y5KqmWkElvQFWVM34bNlmAPOZ9I7SaIPWA6EKToyTI9EsRBKAlYKA==</data>
	</array>
	
me using a specifically generated provisioning profile...

	<key>DeveloperCertificates</key>
	<array>
		<data>MIIFuzCCBKOgAwIBAgIIGUbgCb5Lq+8wDQYJKoZIhvcNAQELBQAwgZYxCzAJBgNVBAYTAlVTMRMwEQYDVQQKDApBcHBsZSBJbmMuMSwwKgYDVQQLDCNBcHBsZSBXb3JsZHdpZGUgRGV2ZWxvcGVyIFJlbGF0aW9uczFEMEIGA1UEAww7QXBwbGUgV29ybGR3aWRlIERldmVsb3BlciBSZWxhdGlvbnMgQ2VydGlmaWNhdGlvbiBBdXRob3JpdHkwHhcNMTkwOTI5MTkzMzIzWhcNMjAwOTI4MTkzMzIzWjCBmTEaMBgGCgmSJomT8ixkAQEMCkwzN1M0WjZCRTkxPDA6BgNVBAMMM0FwcGxlIERpc3RyaWJ1dGlvbjogTmVpbCBLYW5kYWxnYW9ua2FyIChMMzdTNFo2QkU5KTETMBEGA1UECwwKTDM3UzRaNkJFOTEbMBkGA1UECgwSTmVpbCBLYW5kYWxnYW9ua2FyMQswCQYDVQQGEwJVUzCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBAOF8e0GnMnPaJCRzg9c6MOjm99ikbHScCIJBcoyXWkH3PkiRrDy106/gjeLDOtG6psbjKl++TGek+7pP85RKwbHn9vCfu3pqcHe+HZ/LNL2puft4VMObuTHvROkpOSMpoxLZd6iyy+9hADSvhZ+8jaAXe+t3Fz3xicbb+IfA729B32Ly6INDsAfrXHXWPM6uVnpvBd66QGuMFUom+u3b0z7+6Ze5zrkqwsDD0lbokACXyP/OWUoAfpzX5ji8QxxEWfzy0UO5VuNysg7mL/ijK+miDo5XzNglD/xSCo2smF7M7OlO4grMv867jmB9H9r60HRneaWqW/m1gd1nXdJT9G0CAwEAAaOCAgYwggICMAwGA1UdEwEB/wQCMAAwHwYDVR0jBBgwFoAUiCcXCam2GGCL7Ou69kdZxVJUo7cwPwYIKwYBBQUHAQEEMzAxMC8GCCsGAQUFBzABhiNodHRwOi8vb2NzcC5hcHBsZS5jb20vb2NzcDAzLXd3ZHIyMDCCAR0GA1UdIASCARQwggEQMIIBDAYJKoZIhvdjZAUBMIH+MIHDBggrBgEFBQcCAjCBtgyBs1JlbGlhbmNlIG9uIHRoaXMgY2VydGlmaWNhdGUgYnkgYW55IHBhcnR5IGFzc3VtZXMgYWNjZXB0YW5jZSBvZiB0aGUgdGhlbiBhcHBsaWNhYmxlIHN0YW5kYXJkIHRlcm1zIGFuZCBjb25kaXRpb25zIG9mIHVzZSwgY2VydGlmaWNhdGUgcG9saWN5IGFuZCBjZXJ0aWZpY2F0aW9uIHByYWN0aWNlIHN0YXRlbWVudHMuMDYGCCsGAQUFBwIBFipodHRwOi8vd3d3LmFwcGxlLmNvbS9jZXJ0aWZpY2F0ZWF1dGhvcml0eS8wFgYDVR0lAQH/BAwwCgYIKwYBBQUHAwMwHQYDVR0OBBYEFID3YsUR7Hv85KrH+OwrG+tCfjrGMA4GA1UdDwEB/wQEAwIHgDATBgoqhkiG92NkBgEHAQH/BAIFADATBgoqhkiG92NkBgEEAQH/BAIFADANBgkqhkiG9w0BAQsFAAOCAQEAu9o1ms4/A9k5uqhbZRHQoqWXY3n+IbbNKKwUe20mhOvw1zdEGG4YhDmcMR0Mz+e+uRPBpc59SXVZMjcD9tiBQsJS4KHXBpaZVx5B7ERSJQNhIH43hvZnZFddFQyN4hA/9c0TTC92ejIdoGDafEA79fYaYPedGxd6Fkp+LEa9uZvnhPN84xGOO1TV+ozKq1Nz1LJaxYLxu57Ux+fNdL/RJMWw0ZB5wXDdYZNW1qMeIZoNXt/Nz6pA9qhiS0dUs46B2mxms1YdQLsGhqE6PZQEoRJChxZRczoK3y5KqmWkElvQFWVM34bNlmAPOZ9I7SaIPWA6EKToyTI9EsRBKAlYKA==</data>
	</array>
	
?? is this what is selected for other apps??

The benefit of using a wildcard cert is that we wouldn't have to worry about creating a cert for each
individual app
On the other hand, what is the normal practice for Square??
...We could check in the actual Square app that we have
Actual Square Apps use different entitlements for app, watch-appex, watch-app.
And they use fully qualified application identifiers, keychain groups, etc.
(Square also leaves rando entitlement template files lying around in their app lol)

So here's the deal
Why are we even rewriting entitlements at all??? is that necessary?
Why can't we extract entitlements from every kind of app, then do whatever is the needful?
when resigning from one domain to another I guess we may have to exchange some things
what does isign even do with entitlements

what we need: entitlements to create the hash of entitlements in the slot
(sometimes we are rewriting the entitlements)
so what happens is that we special-cased the "top level" app
we got entitlements from that one, then mindlessly rewrote them
what we need to do instead
- get entitlements from every bundle (except frameworks, which don't have them)
- process them similarly
- eliminate "alternate entitlements path" and maybe use this format in the config directory
    entitlements/app-identifier1
    entitlements/app-identifier2


Rethink
- for resigning, we might want to erase entitlements, app id, and replace it with what's in the pprof
- this would imply that we should have different pprofs for each bundle of app, appex, watch app
- but, it seems that the pprof is the same??? so does the pprof in use by Square contain only entitlements for top app?





2) the provisioning profile properties seem to include two different certs





2) The CFBundleVersion needs to be bumped in both IosApp and WatchApp
    
    "Error Domain=ITunesConnectionOperationErrorDomain Code=1091 \"CFBundleVersion Mismatch. The CFBundleVersion value '3' of watch application 'isignTestWatchApp.app/Watch/isignTestWatchApp WatchKit App.app' does not match the CFBundleVersion value '100' of its containing iOS application 'isignTestWatchApp.app'.\" UserInfo={NSLocalizedRecoverySuggestion=CFBundleVersion Mismatch. The CFBundleVersion value '3' of watch application 'isignTestWatchApp.app/Watch/isignTestWatchApp WatchKit App.app' does not match the CFBundleVersion value '100' of its containing iOS application 'isignTestWatchApp.app'., NSLocalizedDescription=CFBundleVersion Mismatch. The CFBundleVersion value '3' of watch application 'isignTestWatchApp.app/Watch/isignTestWatchApp WatchKit App.app' does not match the CFBundleVersion value '100' of its containing iOS application 'isignTestWatchApp.app'., NSLocalizedFailureReason=App Store operation failed.}"