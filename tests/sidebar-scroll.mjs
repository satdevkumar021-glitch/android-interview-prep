import assert from 'node:assert/strict';
import {mkdir} from 'node:fs/promises';
const {chromium}=await import(process.env.PLAYWRIGHT_MODULE||'playwright');
const base=process.env.TEST_BASE_URL||'http://127.0.0.1:8794';
const browser=await chromium.launch(process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH?{executablePath:process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH}:{});
await mkdir('review-artifacts',{recursive:true});
let checks=0;
try {
 for(const viewport of [{width:1280,height:800},{width:1280,height:400},{width:393,height:852},{width:852,height:393}]) {
  const page=await browser.newPage({viewport,reducedMotion:'reduce'});
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.route('https://fonts.googleapis.com/**',route=>route.abort());
  await page.goto(base);await page.locator('#topic-0.active').waitFor();
  const state=()=>page.evaluate(()=>{const s=document.querySelector('.sidebar'),n=document.querySelector('.sidebar-nav');return {y:scrollY,sidebarY:s.getBoundingClientRect().y,logoY:document.querySelector('.sidebar-logo').getBoundingClientRect().y,footerY:document.querySelector('.sidebar-footer').getBoundingClientRect().y,sidebarScroll:s.scrollTop,navScroll:n.scrollTop,navHeight:n.clientHeight,position:getComputedStyle(s).position};});
  const mobile=viewport.width<=900;
  const ids=await page.locator('.nav-link[data-topic]').evaluateAll(links=>links.map(a=>a.dataset.topic));
  for(const id of ids) {
    await page.evaluate(id=>{location.hash='#topic-'+id;},id);
    await page.locator('#topic-'+id+'.active').waitFor();
    await page.evaluate(()=>window.scrollTo({top:0,behavior:'instant'}));
    const before=await state();
    await page.evaluate(()=>window.scrollTo({top:1500,behavior:'instant'}));
    await page.waitForFunction(()=>scrollY>500);
    const after=await state();
    assert.equal(after.position,'fixed');assert.equal(after.sidebarY,before.sidebarY);
    assert.equal(after.logoY,before.logoY);assert.equal(after.sidebarScroll,0);
    assert.equal(after.navScroll,before.navScroll);checks++;
  }
  await page.evaluate(()=>window.scrollTo({top:600,behavior:'instant'}));
  if(mobile){await page.locator('.hamburger').click();assert.equal(await page.locator('.hamburger').getAttribute('aria-expanded'),'true');}
  const beforeNav=await state();assert.ok(beforeNav.navHeight>70,'Topic list remains usable on short screens');
  await page.locator('.sidebar-nav').evaluate(nav=>nav.scrollTop=nav.scrollHeight);
  const scrolledNav=await state();assert.equal(scrolledNav.logoY,beforeNav.logoY);assert.equal(scrolledNav.footerY,beforeNav.footerY);assert.equal(scrolledNav.sidebarScroll,0);
  await page.locator('.sidebar-nav').hover();await page.mouse.wheel(0,1000);
  // Wait for browser wheel dispatch; no app timer is involved in this assertion.
  await page.waitForTimeout(200);const atEnd=await state();assert.equal(atEnd.y,scrolledNav.y,'Sidebar edge must not scroll the article');assert.equal(atEnd.sidebarScroll,0);checks++;
  if(mobile) {
    await page.locator('.main-content').evaluate(main=>main.scrollIntoView({behavior:'instant'}));
    const locked=await state();await page.mouse.move(viewport.width-20,viewport.height/2);await page.mouse.wheel(0,600);await page.waitForTimeout(200);assert.equal((await state()).y,locked.y,'Open drawer locks background wheel scrolling');
    await page.keyboard.press('Escape');assert.equal(await page.locator('.hamburger').getAttribute('aria-expanded'),'false');checks++;
  }
  await page.screenshot({path:`review-artifacts/sidebar-${viewport.width}x${viewport.height}.png`});
  assert.deepEqual(errors,[]);await page.close();
 }
 console.log(`${checks} sidebar checks passed across all 42 routes and four viewports.`);
}finally{await browser.close();}
