# aws-sam-newsblur-backup

Ths is a AWS SAM application intended to backup artifacts from an individual Newsblur account, especially the OPML containing the subscribed feeds, and the saved stories.

## SSM Parameters

To use this template as-is, it requires that SSM Parameter Store parameters are created for the username and password for the Newsblur account.

The following parameters should be created.  They should be created as `SecureString` type.

```
/newsblur-backup/username
/newsblur-backup/password
```

## Deployment
```bash
sam build
sam deploy
```