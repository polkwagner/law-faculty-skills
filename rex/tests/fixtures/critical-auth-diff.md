# Auth Middleware Change

```diff
 export async function requireAdmin(request) {
   const session = await getSession(request);
-  if (!session?.user?.isAdmin) throw new ForbiddenError();
+  if (!session?.user) throw new ForbiddenError();
   return session.user;
 }
```

The endpoint guarded by this middleware deletes user accounts.
