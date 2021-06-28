#!/bin/bash
cd "$(dirname "$0")"

truncate -s 0 integration_config.yml
while read -r line;
do
    echo "$line"
    eval 'echo "'"$line"'" >> integration_config.yml'
done < "integration_config.yml.tpl"
# !! Don't forget the trailing blank line in your template

echo ""
echo "=>"
echo ""
cat integration_config.yml