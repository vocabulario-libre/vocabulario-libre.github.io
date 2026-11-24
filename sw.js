"use strict";
const BASE = self.registration.scope;
const MINE = BASE + "#";
const NAME = MINE + "c3095bda2cbc4dbe8414a92e445474e8bbbe47dad3240a310fedfc8af7e9c246";
const LIST = {
"icon-192.png": "fe82a870290fd25b314c3eb6216d27c0984cb550050cf97590d047b751982b0d",
"icon-512.png": "92f5fea5a55f530e7dab60dd85edb54f643545ae2a982b655741a59550520b39",
"index.en.html": "a9a6030a7304800c264f852e55df89a4b6e3071c3b50bfe05c9ddb21ec0e204d",
"index.html": "265f6dde20946fec7d2ae22e55cdd25169435ce1560dbb5ab63667ca3589554b",
"index.ja.html": "865a918a44c280516c231b409d11c55ff94082d63ba01c751e08f82ff73fcc6a",
"instalar.en.html": "d689c82bebf423ae4d09918f2dae600cbea6f1806826e34efeddc5a0155c353e",
"instalar.html": "38520cfa4ae749e540ba0c890d7bbaaaa9bd4be672407d87496563d9bd262736",
"instalar.ja.html": "f701d42112ee425f293bd9bc21ab76b92e112d037df1f5cd2d5e8124d4457192",
"lecturas/00-lecturas-de-los-libertadores.epub": "8b5979c1ffd0ed9bf759066586001c00775d5c9733969925e02c0082b8c088da",
"lecturas/00-lecturas-de-los-libertadores.md": "701af22be00622a8a65c7f60cfc3879d813af8e6477c365b7caed7e8a21366ad",
"lecturas/00-lecturas-de-los-libertadores.pdf": "0b8f73a562b8448195a19c449cdb3447b399e7c92eb58601ebaaa20ac31783cd",
"lecturas/01-manifiesto-de-cartagena-lectura.epub": "4fb6f9aec23ac4bf375f31cd0ca56a8c24961982432c1b60cb5481013bc80654",
"lecturas/01-manifiesto-de-cartagena-lectura.md": "e81933f93f1266df22c8fc26db35fd9f8955b972756481d7497ec0eb1b974f2c",
"lecturas/01-manifiesto-de-cartagena-lectura.pdf": "74797815af7983765895d9b83b6117fb6682024443c38b7d5b3172159f4fccb4",
"lecturas/01-manifiesto-de-cartagena-register.md": "9b7f04bdd15092d18ec3b67db3678abbf5091ef1dc29e48705a6bd3f180b4742",
"lecturas/02-plan-para-la-reconquista-lectura.epub": "9e8270873c8ad1bb513bfc45ebc3da33d59c8b6e3ca44d231775f1fdecae8379",
"lecturas/02-plan-para-la-reconquista-lectura.md": "7c1d90b65c126345ce8770cb5472374da2011d11ec73e8db2ce8a15a79468495",
"lecturas/02-plan-para-la-reconquista-lectura.pdf": "be670e87778bccf8d624d17aa6eff6aec2be5e895624364204c802a4eb33ac37",
"lecturas/02-plan-para-la-reconquista-register.md": "dbb583ddc92de8a102ada0ab35427d553e6ad487a147d72e9ef9c2511cc06ab3",
"lecturas/03-carta-de-jamaica-lectura.epub": "db251378a9d84f2ecab933b7fe6107fefa9c46976f6897b49222e3d8c09c319c",
"lecturas/03-carta-de-jamaica-lectura.md": "93205393ba2d5a48f3ecd36ba59376ea79ecc3fbec53b1d9845421c162bd949f",
"lecturas/03-carta-de-jamaica-lectura.pdf": "2d142697e09d112977bfc665c1d41df65d420433c355d5e760214782495c3369",
"lecturas/03-carta-de-jamaica-register.md": "579bcf3167e053ad116104868594c124dd06794386ba2e9b6693e94a55fc4711",
"lecturas/04-carta-a-godoy-cruz-lectura.epub": "e6e6248ba011abf3397bed00983d554fa1564d13314803834463584d85faa6b0",
"lecturas/04-carta-a-godoy-cruz-lectura.md": "b2e905798cfd9fc33730b4dc6e8ae42400a5bbf316c48726dc27023b50931ceb",
"lecturas/04-carta-a-godoy-cruz-lectura.pdf": "c6e793bbb5e20fc4ea1443aca5d0047d1c3c9b6733b7a24bfb5c58bda09f30ff",
"lecturas/04-carta-a-godoy-cruz-register.md": "4439ececa856a1b8f2f6f7d4e7c32600b10a867cfe19d107f531d731f3aa85d3",
"lecturas/05-proclamas-partes-y-oficios-lectura.epub": "b61670abc55ab20820426bc609e43eb60594b2cd6b0284d181c2cdb81657039f",
"lecturas/05-proclamas-partes-y-oficios-lectura.md": "8837d8e7fbc3ebdbeb9fa1a12ef9bb7f25d75df9d2ec756e1d742a466e67fcc4",
"lecturas/05-proclamas-partes-y-oficios-lectura.pdf": "d4dba83da207e76ead296fc327fab9abf7aa6e22f5f9e09554c7a3d47e832b6a",
"lecturas/05-proclamas-partes-y-oficios-register.md": "a4c48143a14f12473089af801140abdaec6743b322fa07836789a5887d4fe079",
"lecturas/06-manifiesto-a-las-naciones-lectura.epub": "a03e5ae39ad4ed21b223d86764ee92a5fbfff468ece6806a8db467d5e6d3da34",
"lecturas/06-manifiesto-a-las-naciones-lectura.md": "46085d24dc4b2102a51cae90bff539c709dcbd4da9a73cb766cd41a857c751f5",
"lecturas/06-manifiesto-a-las-naciones-lectura.pdf": "45b2be5e0cf3325a451a45f23a62a669dfb14d2a4537ce2b5dbdcc4ccf404aed",
"lecturas/06-manifiesto-a-las-naciones-register.md": "a6e8dfe838e163ad65c667fab6c73057958428a239f406eb2c0c6d5ab76562c7",
"lecturas/07-discurso-de-angostura-lectura.epub": "65b44978f8af1e247c3428ec4f21305ef79d2e71e3648892741d04e5717d86ae",
"lecturas/07-discurso-de-angostura-lectura.md": "e9c0da12a959203c31b07a1d743ad68244d81289f5e3c5745f3b0698288bf614",
"lecturas/07-discurso-de-angostura-lectura.pdf": "a501c472b9b0f02df70f180d1b76634a6c8eaf465c5484c357c200f4dd7e0bd7",
"lecturas/07-discurso-de-angostura-register.md": "7f93d9a6fcce0ce9e19082fe3c12c68861ae60f84d50d8652dd45d2430a9af03",
"lecturas/08-despedida-del-peru-lectura.epub": "60c7b8b625c410b7794d8e0779075017fa30e3c86353a9141d58946f5621f085",
"lecturas/08-despedida-del-peru-lectura.md": "5d01d8c6b7fa9f5abcef460e4fabe577a38e36c28345ae46caee382a3fd889ef",
"lecturas/08-despedida-del-peru-lectura.pdf": "27d606259e4986898b1e940ea3b292c45b97a7d2acb641b78b1ab8b4082f988b",
"lecturas/08-despedida-del-peru-register.md": "fa1325d0ad42973822e2ea01f8143f7bceb77ab4df11e8c5a264534d596e4dec",
"lecturas/09-mi-delirio-sobre-el-chimborazo-lectura.epub": "367ef5578ea15c1a5d8de7746254bab91bfa852dbdb3826f1dfbe1056235d6eb",
"lecturas/09-mi-delirio-sobre-el-chimborazo-lectura.md": "58e87ff98608654a88f48f89dd7c4c5083d45450aa5abdc92b0edfa09f1b14b3",
"lecturas/09-mi-delirio-sobre-el-chimborazo-lectura.pdf": "887ddc05bcc8165229de7f4c63c3dcdec54f727eee60d469fa435c2e42cdfefc",
"lecturas/09-mi-delirio-sobre-el-chimborazo-register.md": "2d3406d78e3253d6d6ceeb37b0bdf0a5b2623360888ac741ff732f34bcb7c433",
"lecturas/10-discurso-de-abdicacion-lectura.epub": "4d400a3e6ab6db649da328fc1fa2e9050f0174e1a6a9f3d229d57771053fc880",
"lecturas/10-discurso-de-abdicacion-lectura.md": "b6f161fb5e802b708c02885576e45a05e1b240a4fe1dd83147f1eb820831046a",
"lecturas/10-discurso-de-abdicacion-lectura.pdf": "c45606d817bce496b302fee93c077759c90ae2b3c40a919dbe61ad3c4d0aa789",
"lecturas/10-discurso-de-abdicacion-register.md": "28b6b251d68a86dadd046e58c8e7ec1f64e612feba064021d6ec7d2d621b3088",
"lecturas/11-correspondencia-ohiggins-san-martin-lectura.epub": "06ea0c8a6abf45f20ef360dca1fae53cc06eab6dc2780322414bcba00d891dbb",
"lecturas/11-correspondencia-ohiggins-san-martin-lectura.md": "56b05dc3325c9fa9df6af1faa08a038e234b4833cd47524b16103c330a6f7f27",
"lecturas/11-correspondencia-ohiggins-san-martin-lectura.pdf": "9c5f5a98bfaa081b14264eb21ad58657b81e7af956af9fd469631dd1f498e082",
"lecturas/11-correspondencia-ohiggins-san-martin-register.md": "2ec66e9935b15c23fba912891d31fbf7f0db0c79e74f6c0360fd7d5af3d6a91c",
"lecturas/12-maximas-para-mi-hija-lectura.epub": "cf3db6a514929236eb0476f6c4e3b4624b04989fef407b97f41753a1bdcd57dd",
"lecturas/12-maximas-para-mi-hija-lectura.md": "7e3ac42568d1d64ee58532b61c0c8dca683ac73b845327ee1edb72dfe86a6757",
"lecturas/12-maximas-para-mi-hija-lectura.pdf": "2cf22ec60aa5ff82ed3ca704a5f40ddf8b1c66b3ed9d8dc4f4f9f07e91cd5743",
"lecturas/12-maximas-para-mi-hija-register.md": "caebb30344d4062c34141ffb851d82598a694090c6d9c1c34c6d3591fe3e3a87",
"lecturas/13-cartas-de-los-ultimos-anos-lectura.epub": "f1f704371f905cc8c3e3ca5f1bd6c60a01cafabb727adbef47c682eaeeb3405c",
"lecturas/13-cartas-de-los-ultimos-anos-lectura.md": "8a6c153d726d01476bb48d668af6a7d17484e3319d28232b9b13bedf8f8f125b",
"lecturas/13-cartas-de-los-ultimos-anos-lectura.pdf": "5f5a0ef7a9b374d3573f60fc5a6997848eafc55db8229c3b571bb9761c64918c",
"lecturas/13-cartas-de-los-ultimos-anos-register.md": "b91895e2e87b6ce0b71fe388bc7a1f2d4594c40f3d29ba05550a5e367aa1cbfe",
"lecturas/14-cartas-a-miller-lectura.epub": "67032c9b1e180ac544a27e1d2319c6d584b2a05a953fb742a829b5a7d090775e",
"lecturas/14-cartas-a-miller-lectura.md": "89a51fc58f97dae5596370c0958bab8aaeb6661cb01f336ce5e20bac61acc18a",
"lecturas/14-cartas-a-miller-lectura.pdf": "0c0c58bcc285c8d8e523ac7c68ca151c4bc313b0b4c2e3dbdc2743fbeca8bff3",
"lecturas/14-cartas-a-miller-register.md": "1748a78a28cce69cba87ba9c6ca6fbfd57d96aa06b5b46c5094d98fe84558e46",
"lecturas/15-cartas-del-destierro-lectura.epub": "598ab439b53df45dbebd1248217f417ffe9a1ed6a0dc1754a14c6f6ea8a2df52",
"lecturas/15-cartas-del-destierro-lectura.md": "459ce33337094494eaabef918298836aaefa1b446f39980d536f2f5a6fc2ff21",
"lecturas/15-cartas-del-destierro-lectura.pdf": "3e8bb2d656c19310327f5bb0e96ef256f30d989c97e9db30f8832935c79c2a75",
"lecturas/15-cartas-del-destierro-register.md": "d0a77427f2c44aabb52100aa4e64f6981a8b8ff1356169f8c9c67668d0fc1324",
"lecturas/LICENSE": "a2010f343487d3f7618affe54f789f5487602331c0a8d03f49e9a7c547cf0499",
"lecturas/MANIFEST.sha256": "2dacbc75fd08eae51cbd906b8ec55c3d31cac9b0b338c385eae9cfd3a22a710d",
"lecturas/METHOD-grammar-layer.md": "b7c1dc4157819d8a8326e8b731fce5b83382b2b335b66533a864d169fb300345",
"lecturas/METHOD-grammar-layer.pdf": "c72fd2548efc41f15b96e0f173656da14aa90e2e27177f13155f279e4d2707bf",
"lecturas/POLICY-scholarship-and-compliance.md": "3c22ba4b4a2a332848f082f1e14f1382238da9a27e317ab9ee67e92c165bef69",
"lecturas/POLICY-scholarship-and-compliance.pdf": "7b4b73915cbab31fb0c582f8be64d86de33a3edddc53b8c296cb0735b77c0da0",
"lecturas/PRIMER-avestan.epub": "17bd940ea45e6a6cfe687f4d69cd0098949e29dfff25190074b7338bbc7684f8",
"lecturas/PRIMER-avestan.html": "57d139bfad9d4d02a80307755981b715988aa85fcf943f1a8a1bd3707ef28523",
"lecturas/PRIMER-avestan.md": "30cc839f833cabd3ebb5d2836557d18e2d455956afb12df873b719679c525618",
"lecturas/PRIMER-sanskrit.epub": "cd1db05a738adf30887414a73b1a2f49c902374e57f6f960ebdaa14c6de19c06",
"lecturas/PRIMER-sanskrit.html": "eacd6acb480657f3a3f0fc393818c6f8b958b4347201e1264d5c73416caca194",
"lecturas/PRIMER-sanskrit.md": "3d5c7fa9dbb91c3b1a3ccd73c5eede0108535b15e1b5278fac702d1d3f820d99",
"lecturas/PROVENANCE.md": "0ad5d246fa3dfb7d239405ab8338f6d50a9d47f49794d2c0aad79c1b2422e25a",
"lecturas/README.md": "4c39a9de025703f4b106b1dca9243af87be6c6581b8e28cfff434d1e1da0158b",
"lecturas/como-usar.en.html": "f41420f35c86b5632e2f08ffbecbe5a69dcb19342006d28a2e3248d9e726e1a2",
"lecturas/como-usar.html": "ebf86ffa038fd322f9e5baf395a8992b7eefd57e815232e1334f64477e7b1a13",
"lecturas/como-usar.ja.html": "c84b9d1884e3c6ff5970f95854e26d7248a978ba78e79fdaf84c55f3106028f2",
"lecturas/copiar-y-cambiar.en.html": "a0e41d849c0f9814ebe3b2c2916c8a6fd0eb63dc44fafcabbcb34dad9e32c1fb",
"lecturas/copiar-y-cambiar.html": "d190300f24f97504841570b3e820db3e37026ac5eadea74efe4a5a189860fc59",
"lecturas/copiar-y-cambiar.ja.html": "f5856cf1205f1f7fcd1d891961f7e0c50ba26b748bb3602a84e94aefea79afb2",
"lecturas/index.en.html": "adac66d08169b059b2b69aaf784e789c1b2cd20c011669de1920352db2f56ce5",
"lecturas/index.html": "403976473dbe26a5622a1a209cf028d180c51a6239a047dc73c134b71360f7ed",
"lecturas/index.ja.html": "0ccc6d7df23cdeec1a51d29bd9a793b163757677ca31ef04d93bab3dbe45e764",
"lecturas/proximos-cambios.en.html": "f25efa0a0671407fbe1d63daa9db622ab2b0b84562c18885d9294ab032b6f05a",
"lecturas/proximos-cambios.html": "e27de4487fc9434ea3b203d17ce8455c04c79fa92d0ce99cf91e294ab5bea9c0",
"lecturas/proximos-cambios.ja.html": "2ce40449c71b07b1fccd4ed01976a755470e4561cccd30b7509b40623a83e84c",
"lecturas/vocab/flashcards.html": "641656df52ca141d91fbaefdfd9e42b8844a2642319403f69394238183b00092",
"manifest.en.webmanifest": "560145e5e2d242c99efd694095fd443f39ed9a2d751d75f36f0154f55723843c",
"manifest.ja.webmanifest": "f76990bdcb9b07195c1960d52b900480fa2cf3ff525bf2ac85fbd527fc8b2b95",
"manifest.webmanifest": "85eb46d330a59db241acd765c9cd83bcad3dd4ed328f885288f93576212d25d1",
"releases.xml": "ca4faf8e860f9fc79956403e7e99e3d9a6bef777c422d96e889c3bd817e44ed5"
};
const kept = p => Object.prototype.hasOwnProperty.call(LIST, p);
const digest = async b => Array.from(new Uint8Array(await crypto.subtle.digest("SHA-256", b)), x => x.toString(16).padStart(2, "0")).join("");

async function held(names, url, want) {
  for (const name of names) {
    const r = await (await caches.open(name)).match(url);
    if (!r) continue;
    const body = await r.arrayBuffer();
    if (await digest(body) === want) return {name, body, type: r.headers.get("Content-Type")};
  }
  return null;
}

async function make() {
  const names = [NAME].concat((await caches.keys()).filter(n => n.startsWith(MINE) && n !== NAME));
  const copy = await caches.open(NAME);
  for (const [path, want] of Object.entries(LIST)) {
    const url = new URL(path, BASE).href;
    let got = await held(names, url, want);
    if (got && got.name === NAME) continue;
    if (!got) {
      const r = await fetch(url, {cache: "no-store"});
      if (!r.ok || new URL(r.url).origin !== self.location.origin) throw new Error(path);
      const body = await r.arrayBuffer();
      if (await digest(body) !== want) throw new Error(path);
      got = {body, type: r.headers.get("Content-Type")};
    }
    await copy.put(url, new Response(got.body, {headers: got.type ? {"Content-Type": got.type} : {}}));
  }
}

self.addEventListener("install", e => e.waitUntil(make().then(() => self.skipWaiting())));

self.addEventListener("activate", e => e.waitUntil((async () => {
  for (const name of await caches.keys()) if (name.startsWith(MINE) && name !== NAME) await caches.delete(name);
  await self.clients.claim();
})()));

self.addEventListener("fetch", e => {
  if (e.request.method !== "GET" || !e.request.url.startsWith(BASE)) return;
  let p;
  try { p = decodeURIComponent(new URL(e.request.url).pathname.slice(new URL(BASE).pathname.length)); } catch (x) { return; }
  if (p === "" || p.endsWith("/")) p += "index.html";
  if (!kept(p) && kept(p + ".html")) p += ".html";
  if (!kept(p)) return;
  const url = new URL(p, BASE).href;
  e.respondWith(caches.open(NAME).then(c => c.match(url)).then(r => r || fetch(e.request)));
});
