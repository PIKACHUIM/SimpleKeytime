import {Context} from "hono";
import * as saves from './saves'
import * as local from "hono/cookie";
import {Resend} from "resend";


// 获取种子 ###############################################################################
export async function getNonce(c: Context, lens: number = 8) {
    const email = <string>c.req.query('email');
    const setup = <string>c.req.query('setup');
    const reset = <string>c.req.query('reset');
    let user_db: Record<string, any> = await getUsers(c, email);
    const nonce: string = await newNonce(lens);
    // 注册新用户 ========================================================================
    if (setup != undefined && setup.length > 0 && (setup == "1" || setup == "true") ||
        reset != undefined && reset.length > 0 && (reset == "1" || reset == "true")) {
        if (!await Turnstile(c)) return c.json({"nonce": "请先完成验证"}, 403);
        if (Object.keys(user_db).length > 0) {
            let diff: number = Date.now() - user_db[0]["time"]
            let vars: number = Math.floor((300000 - diff) / 60000 + 1)
            if (user_db[0]["flag"] <= 0) {
                if (diff >= 300000) await delUsers(c, email)
                else return c.json(
                    {"nonce": "操作过于频繁\n请等" + vars + "分钟后再试"}, 403)
            } else if (reset == "1" || reset == "true") {
                return c.json(await addUsers(c, email, true))
            } else return c.json(
                {"nonce": "此邮箱已经被注册\n请直接登录\n如忘记密码请重置"}, 400)
        }
        return c.json(await addUsers(c, email)) // 新增真用户
    }
    if (Object.keys(user_db).length > 0) {
        await saves.updateDB(c.env.DB_CF, "Users",
            {code: nonce,},
            {mail: email,});
    }
    return c.json({"nonce": nonce}, 200);
}

// 校验验证 ###############################################################################
export async function Turnstile(c: Context) {
    const authy = <string>c.req.query('authy');
    const SECRET_KEY = c.env.AUTH_KEYS;
    const ip: any = c.req.header("CF-Connecting-IP");
    let formData = new FormData();
    formData.append("secret", SECRET_KEY);
    formData.append("response", authy);
    formData.append("remoteip", ip);
    const url = "https://challenges.cloudflare.com/turnstile/v0/siteverify";
    const result = await fetch(url, {
        body: formData,
        method: "POST",
    });
    const outcome: Record<string, any> = await result.json();
    return outcome.success;

}

// 生成种子 ###############################################################################
export async function newNonce(lens: number = 8): Promise<string> {
    let charset = 'ABCDEFGHJKLMNPQRSTUWXY0123456789';
    let results = '';
    for (let i = 0; i < lens; i++) {
        const randomIndex = Math.floor(Math.random() * charset.length);
        results += charset[randomIndex];
    }
    return results;
}


/* ########################################################################################
*                                     用户数据层操作
######################################################################################## */

// 获取用户 ###############################################################################
export async function getUsers(c: Context, email: string) {
    // console.log(email);
    return await saves.selectDB(c.env.DB_CF, "Users", {mail: {value: email}});
}

// 删除用户 ###############################################################################
export async function delUsers(c: Context, email: string) {
    return await saves.deleteDB(c.env.DB_CF, "Users", {mail: {value: email},});
}

// 新增用户 ###############################################################################
export async function addUsers(c: Context, email: string, reset: boolean = false) {
    const nonce = await newNonce(8);
    if (!reset) {
        await saves.insertDB(c.env.DB_CF, "Users", {
            mail: email,
            code: nonce,
            time: Date.now(),
        });
    } else {
        await saves.updateDB(c.env.DB_CF, "Users", {
            code: nonce,
            time: Date.now(),
        }, {
            mail: email,
        });
    }
    return await codeSend(c, email, nonce)
}


/* ########################################################################################
*                                     用户逻辑层操作
######################################################################################## */

// 用户注册 ###############################################################################
export async function userRegs(c: Context) {
    let mail_data_in: string = <string>c.req.query('email'); // 邮件明文索引用户
    let mail_code_in: string = <string>c.req.query('codes'); // 邮件+验证码 HMAC
    let pass_code_in: string = <string>c.req.query('crypt'); // 密码+验证码 AES2
    let pass_sets_in: string = <string>c.req.query('token'); // 用户+原密码 HMAC
    // 修改密码 ==========================================================================
    if (pass_sets_in != undefined && pass_sets_in.length > 0) {
        if (!await userAuth(c)) return c.json({"flags": 2, "texts": "用户尚未登录"}, 401);
        let user_data_db: Record<string, any>[] = await getUsers(c, mail_data_in);
        if (Object.keys(user_data_db).length <= 0) return c.json({flags: 2}, 401);
        let user_data_in = user_data_db[0]
        console.log(user_data_in['pass'], pass_code_in, pass_sets_in);
        if (user_data_in['pass'] !== pass_code_in) return c.json({flags: 5}, 403);
        await saves.updateDB(c.env.DB_CF, "Users", {pass: pass_sets_in}, {mail: mail_data_in})
        return c.redirect("/login.html", 302);
    }
    // 校验验证码 ========================================================================
    let user_data_db: Record<string, any>[] = await getUsers(c, mail_data_in);
    if (Object.keys(user_data_db).length <= 0)
        return c.json({error: '请先发送邮件验证码'}, 200);
    let user_data_in: Record<string, any> = user_data_db[0]
    let code_hash_db = CryptoJS.SHA256(user_data_in["code"]).toString(CryptoJS.enc.Hex);
    let mail_data_db = CryptoJS.HmacSHA256(mail_data_in, code_hash_db) // 邮箱
    let mail_code_db = mail_data_db.toString(CryptoJS.enc.Hex);
    if (mail_code_db == mail_code_in) { // 验证通过，要保存密码
        try { // 解密密码sha256 ----------------------------------------------------------
            const save_word = CryptoJS.enc.Hex.parse(pass_code_in);
            const save_base = CryptoJS.enc.Base64.stringify(save_word);
            const keys_word = CryptoJS.enc.Hex.parse(code_hash_db);
            // ===========================================================================
            // console.log("save_word", save_word);
            // console.log("save_text", save_text);
            // console.log("save_base", save_base);
            // console.log("keys_word", keys_word);
            // console.log("keys_text", code_hash_db);
            // 执行解密 ==================================================================
            const decrypted = CryptoJS.AES.decrypt(save_base, keys_word, {
                mode: CryptoJS.mode.ECB, padding: CryptoJS.pad.Pkcs7
            });
            const data_text = decrypted.toString(CryptoJS.enc.Hex);
            // console.log("data_word:", decrypted);
            // console.log("data_text:", data_text);
            // 存储密码 =====================================================
            // const pass_salt = bcrypt.genSaltSync(10);
            // const pass_save = bcrypt.hashSync(data_text, pass_salt);
            // console.log("pass_salt:", pass_salt);
            // console.log("pass_save:", pass_save);


            const {publicKey, privateKey} = generateKeyPairSync(
                'ec', {namedCurve: 'prime256v1'});
            console.log(publicKey);
            await saves.updateDB(c.env.DB_CF, "Users",
                {
                    code: "",
                    flag: "1",
                    keys: privateKey.export({type: 'pkcs8', format: 'pem'}),
                    // pass: pass_save,
                    pass: data_text,
                    apis: await newNonce(16),
                    time: Date.now()
                },
                {mail: mail_data_in,}
            );

            return c.redirect("/login.html", 302);
            // return c.json({error: 'OK'}, 200);
        } catch (error) {
            return c.json({error: 'Decryption Failed, ' + error}, 400);
        }
    } else { // 否则验证码错误，验证失败 ==================================================
        return c.json({error: 'Error SMS Code'}, 401);
    }
}

// 用户登录 ###############################################################################
export async function userPost(c: Context) {
    let pass_hmac_in: string = <string>c.req.query('token');
    let mail_data_in: string = <string>c.req.query('email');
    // if (!await Turnstile(c)) return c.json({"nonce": "请先完成验证"}, 403);
    let user_data_db: Record<string, any>[] = await getUsers(c, mail_data_in);
    if (Object.keys(user_data_db).length <= 0) return c.json({flags: 0}, 401);
    let user_data_in = user_data_db[0]
    const pass_hmac_db = await hmacSHA2(user_data_in['pass'], user_data_in['code']);
    if (pass_hmac_db != pass_hmac_in) return c.json({flags: 0, nonce: "用户名密码错误"}, 401);
    // 密码正确设置 Cookie ================================================================
    local.deleteCookie(c, 'users')
    local.setCookie(c, 'mail', mail_data_in);
    await local.setSignedCookie(c, 'auth', pass_hmac_in, user_data_in['pass']);
    await saves.updateDB(c.env.DB_CF, "Users",
        {code: "",},
        {mail: mail_data_in,}
    );
    return c.json({flags: 1});
}

// 验证登录 ###############################################################################
export async function userAuth(c: Context) {
    const user_mail = local.getCookie(c, 'mail')
    // console.log(user_mail);
    if (!user_mail || user_mail.length <= 0) return false;
    const user_data: Record<string, any> = (await getUsers(c, user_mail))[0];
    if (Object.keys(user_data).length <= 2) return false;
    // console.log(user_data);
    const user_auth = await local.getSignedCookie(
        c, user_data["pass"], 'auth')
    // console.log(user_auth);
    return !(!user_auth || user_auth.length <= 0);
}

// 用户退出 ###############################################################################
export async function userExit(c: Context) {
    local.deleteCookie(c, 'mail')
    local.deleteCookie(c, 'auth')
    return c.redirect("/login.html", 302);
}

// 发送验证 ###############################################################################
export async function codeSend(c: Context, mail: string, code: string) {
    return await mailSend(c, mail, "SSL证书助手 - 邮件验证",
        "您正在注册SSL证书助手平台，验证码为：" + code + "，五分钟内有效。")
}

// 发送邮件 ###############################################################################
export async function mailSend(c: Context, email: string, title: string, text: string) {
    try {
        const resend = new Resend(c.env.MAIL_KEYS);
        const {data, error} = await resend.emails.send({
            from: `SSL Helper<${c.env.MAIL_SEND}>`,
            to: [email],
            subject: title,
            html: text,
        });
        if (error) {
            return {"nonce": error.toString()};
        }
        return {"nonce": "邮件发送成功，请查收" + data};
    } catch (error) {
        console.error(error);
        return {"nonce": error};
    }
}

// 生成 HMAC-SHA256 #######################################################################
export async function hmacSHA2(data_text: string, keys_text: string) {
    let temp_data = CryptoJS.HmacSHA256(data_text, keys_text)
    return temp_data.toString(CryptoJS.enc.Hex);
}
