// checks whether or not the url is external to the local site.
// generously provided by StackOverflow: http://stackoverflow.com/questions/6238351/fastest-way-to-detect-external-urls
window.isExternal = function (url) {
    // parse the url into protocol, host, path, query, and fragment. More information can be found here: http://tools.ietf.org/html/rfc3986#appendix-B
    var match = url.match(/^([^:\/?#]+:)?(?:\/\/([^\/?#]*))?([^?#]+)?(\?[^#]*)?(#.*)?/);
    // match[1] matches a protocol if one exists in the url
    // if the protocol in the url does not match the protocol in the window's location, this url is considered external
    if (typeof match[1] === "string" &&
            match[1].length > 0 &&
            match[1].toLowerCase() !== location.protocol)
        return true;
    // match[2] matches the host if one exists in the url
    // if the host in the url does not match the host of the window location, this url is considered external
    if (typeof match[2] === "string" &&
            match[2].length > 0 &&
            // this regex removes the port number if it patches the current location's protocol
            match[2].replace(new RegExp(":("+{"http:":80,"https:":443}[location.protocol]+")?$"), "") !== location.host)
        return true;
    return false;
};

// Utility method for replacing a portion of a string.
window.rewriteStaticLinks = function(content, from, to) {
    if (from === null || to === null) {
        return content;
    }
    // replace only relative urls
    function replacer(match){
        if (match === from){
            return to;
        }
        else {
            return match;
        }
    }
    // change all relative urls only which may be embedded inside other tags in content.
    // handle http and https
    // note: add other protocols here
    var regex = new RegExp("(https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}([-a-zA-Z0-9@:%_\+.~#?&//=]*))?"+from, 'g');
    return content.replace(regex, replacer);
};

// Appends a parameter to a path indicating initial signin
window.appendParameter = function(path, key, value) {
    // Check if the given path already contains a query string by looking for the "?" separator
    if (path.indexOf("?") > -1) {
        // Append signin parameter to the existing query string
        return path + "&" + key + "=" + value;

    }
    else {
        // Append new query string containing the signin parameter
        return path + "?" + key + "=" + value;
    }
};

// Convert a query string to a key/value object
window.parseQueryString = function(queryString) {
    var parameters = {}, queries, pair, i, l;

    // Split the query string into key/value pairs
    queries = queryString.split("&");

    // Break the array of strings into an object
    for (i = 0, l = queries.length; i < l; i++) {
        pair = queries[i].split('=');
        parameters[pair[0]] = pair[1];
    }

    return parameters
};

// Check if the user recently enrolled in a course by looking at a referral URL
window.checkRecentEnrollment = function(referrer) {
    var enrolledIn = null;
    
    // Check if the referrer URL contains a query string
    if (referrer.indexOf("?") > -1) {
        referrerQueryString = referrer.split("?")[1];
    } else {
        referrerQueryString = "";
    }

    if (referrerQueryString != "") {
        // Convert a non-empty query string into a key/value object
        var referrerParameters = window.parseQueryString(referrerQueryString);
        if ("course_id" in referrerParameters && "enrollment_action" in referrerParameters) {
            if (referrerParameters.enrollment_action == "enroll") {
                enrolledIn = referrerParameters.course_id;
            }
        }
    }

    return enrolledIn
}
