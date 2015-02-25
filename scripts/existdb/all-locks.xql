xquery version "3.0";

module namespace services = "http://my/services";

import module namespace transform = "http://exist-db.org/xquery/transform";
declare namespace request="http://exist-db.org/xquery/request";
declare namespace rest = "http://exquery.org/ns/restxq";
declare namespace output = "http://www.w3.org/2010/xslt-xquery-serialization";
declare namespace json="http://www.json.org";

declare
    %rest:GET
    %rest:path("/all-locks.json")
    %rest:produces("application/json")
    %output:method("json")
function services:home-json() {
  services:func()
};

declare
    %rest:GET
    %rest:path("/all-locks.xml")
    %rest:produces("application/xml")
function services:home-xml() {
  services:func()
};

declare function local:trim($arg as xs:string?) as xs:string {
    replace(replace($arg,'\s+$',''),'^\s+','')
} ;

declare
    %private
function services:func() {

    <locks> {
        let $data-collection := '/db'
        for $doc in collection($data-collection)[ends-with(base-uri(.), '.lock.xml')]
        return 
            <lock json:array="true">
                <uri>{base-uri($doc)}</uri>
                <owner>{string($doc//lock/@owner)}</owner>
                <created>{string($doc//lock/@created)}</created>
                <mode>{string($doc//lock/@mode)}</mode>
                <valid>{string($doc//lock/@valid)}</valid>
            </lock>
    }
    </locks>
};

