# Library Management

This module manages books, members, borrows, fines, and email notifications in Odoo.

## Setup

1. Copy `library_management` into your Odoo custom addons path.
2. Add the custom addons path in `addons_path`.
3. Restart the Odoo server.
4. Update the Apps list.
5. Install or upgrade `Library Management`.
6. Make sure the `mail` app is installed.
7. Configure an outgoing email server in Odoo.
8. Set an email address on:
   - the current Odoo user
   - the company
   - the test library member

## Test Data

1. Create at least one library member with a real email address.
2. Create at least two books.
3. Set one book with:
   - `Total Copies = 1`
   - `Available Copies = 1`

## Suggested Demo Data

Use this sample data for quick testing.

### Members

1. Member 1
   - Name: `Raj Patel`
   - Email: your test email
   - State: `Active`

2. Member 2
   - Name: `Asha Mehta`
   - Email: another test email if available
   - State: `Active`

### Books

1. Book 1
   - Title: `Atomic Habits`
   - Author: `James Clear`
   - Category: `Education`
   - Total Copies: `3`
   - Available Copies: `3`

2. Book 2
   - Title: `Clean Code`
   - Author: `Robert C. Martin`
   - Category: `Technology`
   - Total Copies: `1`
   - Available Copies: `1`

3. Book 3
   - Title: `Dune`
   - Author: `Frank Herbert`
   - Category: `Fiction`
   - Total Copies: `2`
   - Available Copies: `2`

## Functional Test Flow

### 1. Borrow confirmation test

1. Issue a normal available book.
2. Confirm the borrow record state becomes `borrowed`.
3. Confirm `available_copies` decreases by 1.
4. Check `Settings > Technical > Email > Emails`.
5. Verify a borrow confirmation email is created.

### 2. Last copy test

1. Issue the book that has only 1 available copy.
2. Confirm it succeeds without validation error.
3. Confirm `available_copies` becomes `0`.

### 3. On-time return test

1. Return a borrowed book before the due date.
2. Confirm the state becomes `returned`.
3. Confirm `available_copies` increases by 1.
4. Confirm no fine is created.

### 4. Overdue notification test

1. Borrow a book.
2. Edit the borrow and set `due_date` to a date before today.
3. Go to `Settings > Technical > Automation > Scheduled Actions`.
4. Open `Library: Mark Overdue Borrows`.
5. Run it manually once.
6. Confirm the borrow state becomes `overdue`.
7. Check `Settings > Technical > Email > Emails`.
8. Verify an overdue notification email is created.

### 5. Fine notification test

1. Return an overdue borrowed book.
2. Confirm a fine record is created.
3. Confirm a fine notification email is created.
4. Confirm the member becomes blocked.

### 6. Fine payment test

1. Open the created fine.
2. Pay the full amount.
3. Confirm fine state becomes `paid`.
4. Confirm the member is unblocked if there are no other unpaid fines.

## Email Verification

After each email-related action:

1. Open `Settings > Technical > Email > Emails`.
2. Check the newest email record.
3. Confirm the status is one of:
   - `Sent`
   - `Outgoing`
   - `Delivery Failed`
4. If using Gmail, also check:
   - Inbox
   - Spam
   - Promotions tab

## Edge Cases

1. Member without email:
   - Borrow should still work
   - No email should be sent
2. Blocked member:
   - Borrow must be prevented
3. Same member tries to borrow the same unreturned book:
   - Validation error must appear
4. Book with `Available Copies = 0`:
   - Borrow must be prevented

## Expected Features

- Borrow confirmation email on book issue
- Overdue email when scheduled action marks a borrow overdue
- Fine email when an overdue book is returned
- Automatic member blocking on fine creation
- Automatic member unblocking after full payment of all fines

## If Something Fails

Please report:

1. The exact step that failed
2. Any Odoo popup error
3. Any traceback from the server log
4. The status and failure reason from `Settings > Technical > Email > Emails`
