const links = document.querySelectorAll("div#plaintext li a");
let links_arr = [];
for (let link of links) {
    links_arr.push(link.href);
}

links_arr
