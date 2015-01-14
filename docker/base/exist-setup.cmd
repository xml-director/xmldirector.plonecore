spawn java -jar eXist-db-setup-2.2.jar -console
expect "Select target" { send "/home/plone/exist\n" }
expect "press 1" { send "1\n" }
expect "Data dir" { send "/home/plone/exist-datat\n" }
expect "press 1" { send "1\n" }
expect "Enter password" { send "admin\n" }
expect "Enter password" { send "admin\n" }
expect "Maximum memory" { send "\n" }
expect "Cache memory" { send "\n" }
expect "press 1" {
    send "1\n"
}
expect -timeout -1 "Console installation done" {
    wait
    exit
}

