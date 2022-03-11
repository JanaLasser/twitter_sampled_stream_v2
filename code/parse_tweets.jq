jq -r '[.id, .conversation_id, .author_id, .created_at, .__twarc.retrieved_at, .source, .lang, (.text | gsub("\n";" ")), (try .referenced_tweets[0] | "\(.type)", "\(.id)"), .author.created_at, .author.location, .author.name, .author.username, .author.verified, .author.protected, .author.public_metrics.followers_count, .author.public_metrics.following_count, .author.public_metrics.tweet_count, .author.public_metrics.listed_count] | @csv'