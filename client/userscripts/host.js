// ==UserScript==
// @include https://remanga.org/panel/add-titles/
// @include http://localhost:8080/add-title/
// ==/UserScript==


(function(w) {
    let Browser = null
    let Controller = null

    new QWebChannel(qt.webChannelTransport, function (channel) {
        Browser = channel.objects.backend
        Controller = channel.objects.controller
    })

    const isInViewport = function(element) {
        const bounding = element.getBoundingClientRect()
        return (
            bounding.top >= 0 &&
            bounding.left >= 0 &&
            bounding.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
            bounding.right <= (window.innerWidth || document.documentElement.clientWidth)
        )
    }

    const _scrollToElement = function(element) {
        element.scrollIntoView()
        return element.getBoundingClientRect()
    }

    const wait = async function(timeout) {
        return new Promise(resolve => {
            window.setTimeout(resolve, timeout)
        })
    }

    const repeat = async function (n_times, func) {
        while (n_times > 0) {
            try {
                await func()
                return Promise.resolve()

            } catch (e) {
                n_times--
                await wait(10)
            }
        }
    }

    function clickTo(element) {
        if (typeof element == 'string') {
            element = document.querySelector(element)
        }

        return new Promise(resolve => {
            const {x, y, width, height} = _scrollToElement(element)
            Browser.clickTo([x + width / 2, y + height / 2], resolve)
        })
    }

    async function type(element, text) {
        if (typeof element == 'string') {
            element = document.querySelector(element)
        }

        await clickTo(element)

        return new Promise(resolve => {
            Browser.typeText(text, resolve)
        })
    }

    async function pressKey(keyCode) {
        return new Promise(resolve => {
            Browser.sendKey(keyCode, resolve)
        })
    }

    w.completeAndSend = async function(data) {
        if (!w.readyForUse)
            await jQueryFill()

        const title = JSON.parse(data)

        await wait(100)

        await clickTo('#id_cover')

        document.forms[0].en_name['value'] = title.eng_title
        document.forms[0].rus_name['value'] = title.rus_title
        document.forms[0].another_name['value'] = title.kor_title
        document.forms[0].original_link['value'] = 'http://seoji.nl.go.kr/landingPage?isbn=' + title.isbn

        await wait(200)

        await clickTo('form > div > button[type="submit"]')

    }

    async function eventsEmulatedFill() {
        document.forms[0].type['value'] = 1
        document.forms[0].status['value'] = 4
        document.forms[0].age_limit['value'] = 0
        document.forms[0].issue_year['value'] = 2021
        // document.forms[0].action = 'https://httpbin.org/post'
        // document.forms[0].action = 'http://localhost:8080/add-title/'

        await wait(300)

        await repeat(3, async () => {
            await clickTo('#id_categories_chosen')
            await clickTo('#id_categories_chosen > div > ul > li:nth-child(1)')
        })

        await wait(300)

        await repeat(3, async () => {
            await clickTo('#id_categories_chosen')
            await clickTo('#id_categories_chosen > div > ul > li:nth-child(2)')
        })

        await wait(300)

        await repeat(3, async () => {
            await clickTo('#id_genres_chosen')
            await clickTo('#id_genres_chosen > div > ul > li:nth-child(21)')
        })

        await wait(300)

        await type('#id_publishers_chosen', 'PULSAR')
        await pressKey('Key_Return')

        await wait(200)

        document.querySelector('#id_genres > option[value="23"]').selected = true
        // 6275 (1337 team) | 5992 (PULSAR team)
        document.querySelector('#id_publishers > option[value="5992"]').selected = true
        document.querySelector('#id_categories > option[value="6"]').selected = true
        document.querySelector('#id_categories > option[value="5"]').selected = true

        w.readyForUse = true
    }

    async function jQueryFill() {
        await wait(200)

        $.expr[':'].textEquals = $.expr.createPseudo(function (arg) {
            return function (elem) {
                return $(elem).text().match("^" + arg + "$")
            }
        })


        $('#id_age_limit').val('0')
        $('#id_issue_year').val('2021')
        $('#id_status').val('4')

        $('#id_type').find("option:textEquals('Манхва')").attr('selected', 'selected')
        $('#id_genres').find("option:textEquals('Приключения')").attr('selected', 'selected')
        // TEAM
        $('#id_publishers').find("option:textEquals('PULSAR')").attr('selected', 'selected')
        $('#id_categories').find("option:textEquals('В цвете')").attr('selected', 'selected')
        $('#id_categories').find("option:textEquals('Веб')").attr('selected', 'selected')

        $('#id_genres').trigger("chosen:updated")
        $('#id_publishers').trigger("chosen:updated")
        $('#id_authors').trigger("chosen:updated")
        $('#id_teams').trigger("chosen:updated")
        $('#id_categories').trigger("chosen:updated")

        await _scrollToElement(document.querySelector('#id_cover'))
        await wait(300)

        w.readyForUse = true
    }

    document.addEventListener('DOMContentLoaded', async function () {
        const getStatus = async (hasStatusCallback, callback) => {
            let message = ''

            message = 'Спасибо за помощь проекту, ваш запрос отправлен на модерацию'
            if (
                window.find(message, false, false) ||
                window.find(message, false, true)
            ) return await hasStatusCallback('success', message)

            message = 'Тайтл с таким Английское название уже существует'
            if (
                window.find(message, false, false) ||
                window.find(message, false, true)
            ) return await hasStatusCallback('error', message)

            message = 'Тайтл с таким Русское название уже существует'
            if (
                window.find(message, false, false) ||
                window.find(message, false, true)
            ) return await hasStatusCallback('error', message)

            message = 'Тайтл с таким Другое название уже существует'
            if (
                window.find(message, false, false) ||
                window.find(message, false, true)
            ) return await hasStatusCallback('error', message)

            return await callback()
        }

        await repeat(10, async () => {
            if (Controller === null)
                throw new Error()
        })

        await getStatus(
            async (status, message) => {
                Controller.titleSentEmit(JSON.stringify({
                    status,
                    message,
                    timestamp: Date.now()
                }))
            },
            async () => {
                Controller.completeAndSend.connect(completeAndSend)
                await jQueryFill()

                Controller.tabReadyEmit()
            }
        )

    })

})(window)
