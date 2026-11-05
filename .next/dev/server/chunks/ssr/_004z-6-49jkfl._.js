(()=>{"use strict";module.exports = [
"[project]/node_modules/.pnpm/next@16.4.2_@types+node@24.12.3_react-dom@19.3.1_react@19.3.1__react@19.3.1_sass@1.77.4/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react-jsx-dev-runtime.js [app-ssr] (ecmascript)", ((__turbopack_context__, module, exports) => {
"use strict";

module.exports = __turbopack_context__.r("[project]/node_modules/.pnpm/next@16.4.2_@types+node@24.12.3_react-dom@19.3.1_react@19.3.1__react@19.3.1_sass@1.77.4/node_modules/next/dist/server/route-modules/app-page/module.compiled.js [app-ssr] (ecmascript)").vendored['react-ssr'].ReactJsxDevRuntime;
}),
"[project]/src/app/(frontend)/page.tsx [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "default",
    ()=>HomePage
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$16$2e$4$2e$2_$40$types$2b$node$40$24$2e$12$2e$3_react$2d$dom$40$19$2e$3$2e$1_react$40$19$2e$3$2e$1_$5f$react$40$19$2e$3$2e$1_sass$40$1$2e$77$2e$4$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/.pnpm/next@16.4.2_@types+node@24.12.3_react-dom@19.3.1_react@19.3.1__react@19.3.1_sass@1.77.4/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react-jsx-dev-runtime.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$16$2e$4$2e$2_$40$types$2b$node$40$24$2e$12$2e$3_react$2d$dom$40$19$2e$3$2e$1_react$40$19$2e$3$2e$1_$5f$react$40$19$2e$3$2e$1_sass$40$1$2e$77$2e$4$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/.pnpm/next@16.4.2_@types+node@24.12.3_react-dom@19.3.1_react@19.3.1__react@19.3.1_sass@1.77.4/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react.js [app-ssr] (ecmascript)");
// This starter uses client state for its pointer effect. When replacing it,
// remove 'use client' unless the new page needs browser APIs, event handlers,
// or React client hooks.
'use client';
;
;
function HomePage() {
    const [hovering, setHovering] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$16$2e$4$2e$2_$40$types$2b$node$40$24$2e$12$2e$3_react$2d$dom$40$19$2e$3$2e$1_react$40$19$2e$3$2e$1_$5f$react$40$19$2e$3$2e$1_sass$40$1$2e$77$2e$4$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])(false);
    const [cursor, setCursor] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$16$2e$4$2e$2_$40$types$2b$node$40$24$2e$12$2e$3_react$2d$dom$40$19$2e$3$2e$1_react$40$19$2e$3$2e$1_$5f$react$40$19$2e$3$2e$1_sass$40$1$2e$77$2e$4$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])({
        x: 0,
        y: 0
    });
    const handlePointerMove = (event)=>{
        const rect = event.currentTarget.getBoundingClientRect();
        setCursor({
            x: event.clientX - rect.left,
            y: event.clientY - rect.top
        });
    };
    // The hover layer is the same dot grid scaled up, revealed only within a soft
    // circle that follows the cursor — so dots appear to bloom under the pointer.
    const mask = `radial-gradient(circle at ${cursor.x}px ${cursor.y}px, #000 72px, transparent 120px)`;
    const container = {
        position: 'relative',
        width: '100%',
        minHeight: '100vh',
        overflow: 'hidden',
        backgroundColor: '#f8fbff'
    };
    const dots = {
        position: 'absolute',
        inset: 0,
        backgroundImage: 'radial-gradient(circle at center, rgba(157, 200, 255, 0.52) 1.2px, transparent 1.4px)',
        backgroundPosition: 'center',
        backgroundSize: '18px 18px'
    };
    const dotsHover = {
        position: 'absolute',
        inset: 0,
        backgroundImage: 'radial-gradient(circle at center, rgba(157, 200, 255, 0.52) 2.16px, transparent 2.36px)',
        backgroundPosition: 'center',
        backgroundSize: '18px 18px',
        opacity: hovering ? 1 : 0,
        maskImage: mask,
        WebkitMaskImage: mask
    };
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$16$2e$4$2e$2_$40$types$2b$node$40$24$2e$12$2e$3_react$2d$dom$40$19$2e$3$2e$1_react$40$19$2e$3$2e$1_$5f$react$40$19$2e$3$2e$1_sass$40$1$2e$77$2e$4$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("main", {
        style: container,
        onPointerEnter: ()=>setHovering(true),
        onPointerMove: handlePointerMove,
        onPointerLeave: ()=>setHovering(false),
        children: [
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$16$2e$4$2e$2_$40$types$2b$node$40$24$2e$12$2e$3_react$2d$dom$40$19$2e$3$2e$1_react$40$19$2e$3$2e$1_$5f$react$40$19$2e$3$2e$1_sass$40$1$2e$77$2e$4$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                style: dots
            }, void 0, false, {
                fileName: "[project]/src/app/(frontend)/page.tsx",
                lineNumber: 55,
                columnNumber: 7
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$16$2e$4$2e$2_$40$types$2b$node$40$24$2e$12$2e$3_react$2d$dom$40$19$2e$3$2e$1_react$40$19$2e$3$2e$1_$5f$react$40$19$2e$3$2e$1_sass$40$1$2e$77$2e$4$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                style: dotsHover
            }, void 0, false, {
                fileName: "[project]/src/app/(frontend)/page.tsx",
                lineNumber: 56,
                columnNumber: 7
            }, this)
        ]
    }, void 0, true, {
        fileName: "[project]/src/app/(frontend)/page.tsx",
        lineNumber: 49,
        columnNumber: 5
    }, this);
}
}),
];})()

//# sourceMappingURL=_004z-6-49jkfl._.js.map