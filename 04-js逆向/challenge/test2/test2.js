function sdk_2(){
window = this;
window.btoa = require('btoa')
var hexcase = 0;  /* hex output format. 0 - lowercase; 1 - uppercase        */
var b64pad  = ""; /* base-64 pad character. "=" for strict RFC compliance   */
var chrsz   = 8;  /* bits per input character. 8 - ASCII; 16 - Unicode      */
function safe_add(x, y)
{
  var lsw = (x & 0xFFFF) + (y & 0xFFFF);
  var msw = (x >> 16) + (y >> 16) + (lsw >> 16);
  return (msw << 16) | (lsw & 0xFFFF);
}
function bit_rol(num, cnt)
{
  return (num << cnt) | (num >>> (32 - cnt));
}
function md5_cmn(q, a, b, x, s, t)
{
  return safe_add(bit_rol(safe_add(safe_add(a, q), safe_add(x, t)), s),b);
}
function md5_ff(a, b, c, d, x, s, t)
{
  return md5_cmn((b & c) | ((~b) & d), a, b, x, s, t);
}
function md5_gg(a, b, c, d, x, s, t)
{
  return md5_cmn((b & d) | (c & (~d)), a, b, x, s, t);
}
function md5_hh(a, b, c, d, x, s, t)
{
  return md5_cmn(b ^ c ^ d, a, b, x, s, t);
}
function md5_ii(a, b, c, d, x, s, t)
{
  return md5_cmn(c ^ (b | (~d)), a, b, x, s, t);
}
function core_md5(x, len)
{
  /* append padding */
  x[len >> 5] |= 0x80 << ((len) % 32);
  x[(((len + 64) >>> 9) << 4) + 14] = len;

  var a =  1732584193;
  var b = -271733879;
  var c = -1732584194;
  var d =  271733878;

  for(var i = 0; i < x.length; i += 16)
  {
    var olda = a;
    var oldb = b;
    var oldc = c;
    var oldd = d;

    a = md5_ff(a, b, c, d, x[i+ 0], 7 , -680876936);
    d = md5_ff(d, a, b, c, x[i+ 1], 12, -389564586);
    c = md5_ff(c, d, a, b, x[i+ 2], 17,  606105819);
    b = md5_ff(b, c, d, a, x[i+ 3], 22, -1044525330);
    a = md5_ff(a, b, c, d, x[i+ 4], 7 , -176418897);
    d = md5_ff(d, a, b, c, x[i+ 5], 12,  1200080426);
    c = md5_ff(c, d, a, b, x[i+ 6], 17, -1473231341);
    b = md5_ff(b, c, d, a, x[i+ 7], 22, -45705983);
    a = md5_ff(a, b, c, d, x[i+ 8], 7 ,  1770035416);
    d = md5_ff(d, a, b, c, x[i+ 9], 12, -1958414417);
    c = md5_ff(c, d, a, b, x[i+10], 17, -42063);
    b = md5_ff(b, c, d, a, x[i+11], 22, -1990404162);
    a = md5_ff(a, b, c, d, x[i+12], 7 ,  1804603682);
    d = md5_ff(d, a, b, c, x[i+13], 12, -40341101);
    c = md5_ff(c, d, a, b, x[i+14], 17, -1502002290);
    b = md5_ff(b, c, d, a, x[i+15], 22,  1236535329);

    a = md5_gg(a, b, c, d, x[i+ 1], 5 , -165796510);
    d = md5_gg(d, a, b, c, x[i+ 6], 9 , -1069501632);
    c = md5_gg(c, d, a, b, x[i+11], 14,  643717713);
    b = md5_gg(b, c, d, a, x[i+ 0], 20, -373897302);
    a = md5_gg(a, b, c, d, x[i+ 5], 5 , -701558691);
    d = md5_gg(d, a, b, c, x[i+10], 9 ,  38016083);
    c = md5_gg(c, d, a, b, x[i+15], 14, -660478335);
    b = md5_gg(b, c, d, a, x[i+ 4], 20, -405537848);
    a = md5_gg(a, b, c, d, x[i+ 9], 5 ,  568446438);
    d = md5_gg(d, a, b, c, x[i+14], 9 , -1019803690);
    c = md5_gg(c, d, a, b, x[i+ 3], 14, -187363961);
    b = md5_gg(b, c, d, a, x[i+ 8], 20,  1163531501);
    a = md5_gg(a, b, c, d, x[i+13], 5 , -1444681467);
    d = md5_gg(d, a, b, c, x[i+ 2], 9 , -51403784);
    c = md5_gg(c, d, a, b, x[i+ 7], 14,  1735328473);
    b = md5_gg(b, c, d, a, x[i+12], 20, -1926607734);

    a = md5_hh(a, b, c, d, x[i+ 5], 4 , -378558);
    d = md5_hh(d, a, b, c, x[i+ 8], 11, -2022574463);
    c = md5_hh(c, d, a, b, x[i+11], 16,  1839030562);
    b = md5_hh(b, c, d, a, x[i+14], 23, -35309556);
    a = md5_hh(a, b, c, d, x[i+ 1], 4 , -1530992060);
    d = md5_hh(d, a, b, c, x[i+ 4], 11,  1272893353);
    c = md5_hh(c, d, a, b, x[i+ 7], 16, -155497632);
    b = md5_hh(b, c, d, a, x[i+10], 23, -1094730640);
    a = md5_hh(a, b, c, d, x[i+13], 4 ,  681279174);
    d = md5_hh(d, a, b, c, x[i+ 0], 11, -358537222);
    c = md5_hh(c, d, a, b, x[i+ 3], 16, -722521979);
    b = md5_hh(b, c, d, a, x[i+ 6], 23,  76029189);
    a = md5_hh(a, b, c, d, x[i+ 9], 4 , -640364487);
    d = md5_hh(d, a, b, c, x[i+12], 11, -421815835);
    c = md5_hh(c, d, a, b, x[i+15], 16,  530742520);
    b = md5_hh(b, c, d, a, x[i+ 2], 23, -995338651);

    a = md5_ii(a, b, c, d, x[i+ 0], 6 , -198630844);
    d = md5_ii(d, a, b, c, x[i+ 7], 10,  1126891415);
    c = md5_ii(c, d, a, b, x[i+14], 15, -1416354905);
    b = md5_ii(b, c, d, a, x[i+ 5], 21, -57434055);
    a = md5_ii(a, b, c, d, x[i+12], 6 ,  1700485571);
    d = md5_ii(d, a, b, c, x[i+ 3], 10, -1894986606);
    c = md5_ii(c, d, a, b, x[i+10], 15, -1051523);
    b = md5_ii(b, c, d, a, x[i+ 1], 21, -2054922799);
    a = md5_ii(a, b, c, d, x[i+ 8], 6 ,  1873313359);
    d = md5_ii(d, a, b, c, x[i+15], 10, -30611744);
    c = md5_ii(c, d, a, b, x[i+ 6], 15, -1560198380);
    b = md5_ii(b, c, d, a, x[i+13], 21,  1309151649);
    a = md5_ii(a, b, c, d, x[i+ 4], 6 , -145523070);
    d = md5_ii(d, a, b, c, x[i+11], 10, -1120210379);
    c = md5_ii(c, d, a, b, x[i+ 2], 15,  718787259);
    b = md5_ii(b, c, d, a, x[i+ 9], 21, -343485551);

    a = safe_add(a, olda);
    b = safe_add(b, oldb);
    c = safe_add(c, oldc);
    d = safe_add(d, oldd);
  }
  return Array(a, b, c, d);

}
function str2binl(str)
{
  var bin = Array();
  var mask = (1 << chrsz) - 1;
  for(var i = 0; i < str.length * chrsz; i += chrsz)
    bin[i>>5] |= (str.charCodeAt(i / chrsz) & mask) << (i%32);
  return bin;
}
function binl2hex(binarray)
{
  var hex_tab = hexcase ? "0123456789ABCDEF" : "0123456789abcdef";
  var str = "";
  for(var i = 0; i < binarray.length * 4; i++)
  {
    str += hex_tab.charAt((binarray[i>>2] >> ((i%4)*8+4)) & 0xF) +
           hex_tab.charAt((binarray[i>>2] >> ((i%4)*8  )) & 0xF);
  }
  return str;
}

function hex_md5(s){ return binl2hex(core_md5(str2binl(s), s.length * chrsz));}


var _$oa = ['RWhHeWs=', 'U3R5REs=', 'YWlkaW5nX3dpbg==', 'd052Rkc=', 'd2xXemo=', 'YWN0aW9u', 'RHlTQlU=', 'Z0xXelo=', 'cExtRks=', 'QUhTVGQ=', 'dUdJSUk=', 'OyBwYXRoPS8=', 'RkpUVUk=', 'eGdIVWI=', 'b0ZPYkQ=', 'WWV4SVI=', 'blppZnk=', 'Uk9vaXE=', 'cUFaWG0=', 'dk1ISHM=', 'c2lnbj0=', 'dVl2alg=', 'QlhLbVA=', 'WllGUWU=', 'RlhmVEc=', 'dGdkT3Y=', 'Z2dlcg==', 'Y29uc3RydWN0b3I=', 'ZHpWQmk=', 'aXBqdEw=', 'cm91bmQ=', 'QXhteHU=', 'Y291bnRlcg==', 'YnRvYQ==', 'Y2FsbA==', 'WGpTQUM=', 'd2NITWs=', 'a1hZZW0=', 'Z3RHUmE=', 'VUdreUk=', 'd2FpRGw=', 'Q2hST2E=', 'eU5LcVU=', 'bUxpQVA=', 'S0xyQ0g=', 'cENMam4=', 'dlF5aUs=', 'TmtRaGI=', 'ZUNFUm4=', 'cUtLQ0s=', 'ZFBqZWs=', 'bG9n', 'ZktoTXE=', 'bXFTUkY=', 'SG1KWlA=', 'YXBwbHk=', 'TmlPZ0c=', 'cUhYcXo=', 'dm1pWmI=', 'dmdlTkU=', 'c3RyaW5n', 'WFJhdmg=', 'bHFBS1Y=', 'ZVd0am4=', 'SER6YVA=', 'ZGVidQ==', 'anNTQ2o=', 'cXBUWHA=', 'Y1RuYXI=', 'cHRvRmY=', 'cmVsb2Fk', 'Z2ZaV2s=', 'VUtGZFM=', 'T1RYY3E=', '5q2k572R6aG15Y+X44CQ54ix6ZSt5LqR55u+IFYxLjAg5Yqo5oCB54mI44CR5L+d5oqk', 'UnBBQmI=', 'YkxkZnA=', 'ZlhlSlg=', 'ZFNuamU=', 'Y2hhaW4=', 'ZnVuY3Rpb24gKlwoICpcKQ==', 'b0pwd2U=', 'U0hJVGU=', 'V0RnTUk=', 'UmFJdEk=', 'QnFrTGU=', 'UVBGSGI=', 'RW1nY1I=', 'c3RhdGVPYmplY3Q=', 'd2hpbGUgKHRydWUpIHt9', 'bHJMUmM=', 'TEtiS3E=', 'RFN0Wmo=', 'bGVuZ3Ro', 'bGlTVGQ=', 'S1lBQ3o=', 'QlRtdlU=', 'cmpIUUw=', 'd3dBVW8='];
    (function(a, b) {
        var c = function(f) {
            while (--f) {
                a['push'](a['shift']());
            }
        };
        c(++b);
    }(_$oa, 0x128));

var _$ob = function(a, b) {
        a = a - 0x0;
        var c = _$oa[a];
        if (_$ob['cMwOBs'] === undefined) {
            (function() {
                var e = function() {
                    var h;
                    try {
                        h = Function('return\x20(function()\x20' + '{}.constructor(\x22return\x20this\x22)(\x20)' + ');')();
                    } catch (i) {
                        h = window;
                    }
                    return h;
                };
                var f = e();
                var g = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=';
                f['atob'] || (f['atob'] = function(h) {
                    var i = String(h)['replace'](/=+$/, '');
                    var j = '';
                    for (var k = 0x0, l, m, n = 0x0; m = i['charAt'](n++); ~m && (l = k % 0x4 ? l * 0x40 + m : m,
                    k++ % 0x4) ? j += String['fromCharCode'](0xff & l >> (-0x2 * k & 0x6)) : 0x0) {
                        m = g['indexOf'](m);
                    }
                    return j;
                }
                );
            }());
            _$ob['QnKkcP'] = function(e) {
                var f = atob(e);
                var g = [];
                for (var h = 0x0, j = f['length']; h < j; h++) {
                    g += '%' + ('00' + f['charCodeAt'](h)['toString'](0x10))['slice'](-0x2);
                }
                return decodeURIComponent(g);
            }
            ;
            _$ob['xLGfYD'] = {};
            _$ob['cMwOBs'] = !![];
        }
        var d = _$ob['xLGfYD'][a];
        if (d === undefined) {
            c = _$ob['QnKkcP'](c);
            _$ob['xLGfYD'][a] = c;
        } else {
            c = d;
        }
        return c;
    };
var a = {
            'yNKqU': function(d, e) {
                return d + e;
            },
            'UGkyI': 'debu',
            'NkQhb': _$ob('0x1b'),
            'ROoiq': _$ob('0x59'),
            'uYvjX': function(d, e) {
                return d === e;
            },
            'tgdOv': _$ob('0x27'),
            'OTLbW': 'VcBka',
            'uGIII': function(d, e) {
                return d !== e;
            },
            'lQoKr': _$ob('0x43'),
            'OTXcq': _$ob('0x44'),
            'waNig': _$ob('0x46'),
            'vQyiK': _$ob('0x51'),
            'vgeNE': '\x5c+\x5c+\x20*(?:[a-zA-Z_$][0-9a-zA-Z_$]*)',
            'YexIR': function(d, e) {
                return d(e);
            },
            'rjHQL': 'init',
            'dzVBi': function(d, e) {
                return d + e;
            },
            'bLdfp': _$ob('0x50'),
            'lDlMm': function(d, e) {
                return d + e;
            },
            'BqkLe': 'input',
            'wlWzj': function(d, e) {
                return d === e;
            },
            'HmJZP': _$ob('0xd'),
            'tZTPH': _$ob('0x20'),
            'UKFdS': function(d, e) {
                return d(e);
            },
            'NiOgG': function(d) {
                return d();
            },
            'lqUPB': function(d, e) {
                return d + e;
            },
            'HVAFP': _$ob('0x6'),
            'AHSTd': _$ob('0x4f'),
            'oJpwe': function(d, e, f) {
                return d(e, f);
            },
            'vmiZb': _$ob('0x4b'),
            'lrLRc': function(d, e) {
                return d + e;
            },
            'ZYFQe': _$ob('0x3'),
            'RpABb': function(d, e) {
                return d(e);
            },
            'liSTd': function(d, e) {
                return d(e);
            },
            'BTmvU': function(d, e) {
                return d(e);
            },
            'aIuEI': function(d, e) {
                return d / e;
            },
            'bCsbN': function(d, e) {
                return d + e;
            },
            'mLiAP': function(d, e) {
                return d + e;
            },
            'wwAUo': function(d, e) {
                return d + e;
            },
            'fKhMq': _$ob('0x15'),
            'ipjtL': function(d, e) {
                return d / e;
            },
            'uYAgC': _$ob('0xc')
        };
token = window[_$ob('0x22')](a['lrLRc'](a[_$ob('0x18')], a[_$ob('0x4c')](String, c)));
var c = new Date()['valueOf']();
md = a[_$ob('0x5f')](hex_md5, window[_$ob('0x22')](a[_$ob('0x5b')](a['ZYFQe'], a[_$ob('0x61')](String, Math[_$ob('0x1f')](a['aIuEI'](c, 0x3e8))))));
var cookie = a['bCsbN'](a[_$ob('0x2c')](a[_$ob('0x2c')](a[_$ob('0x2c')](a[_$ob('0x0')](a[_$ob('0x0')](a[_$ob('0x35')], Math[_$ob('0x1f')](a[_$ob('0x1e')](c, 0x3e8))), '~'), token), '|'), md), a['uYAgC']);
return cookie
}

console.log(sdk_2())