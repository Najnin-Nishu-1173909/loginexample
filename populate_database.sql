BEGIN;

TRUNCATE TABLE project_members, tasks, projects, users
RESTART IDENTITY CASCADE;

INSERT INTO users (
    email,
    first_name,
    last_name,
    position,
    profile_picture,
    password_hash,
    user_role,
    status
)
VALUES
    ('aarav.anderson@lincolnuni.ac.nz', 'Aarav', 'Anderson', 'Bachelor of Commerce Student', NULL, '$2y$12$AGSeN/eF02cFyjfzlogQxuSQ2YBvgXydkHcThYz6LXL3aIn3hu48e', 'student', 'active'),
    ('aisha.baker@lincolnuni.ac.nz', 'Aisha', 'Baker', 'Master of Applied Computing Student', NULL, '$2y$12$4YQcS5AAyQq.heqjT0opsedVLH/mzUDzcImvwj7ZBHa0GZq9immUy', 'student', 'active'),
    ('akira.chen@lincolnuni.ac.nz', 'Akira', 'Chen', 'Bachelor of Agricultural Science Student', NULL, '$2y$12$4hctK21lfSBwUMGmdJeL/eroqedqvFcjAQhBc7RU5931mR8iRSwqC', 'student', 'active'),
    ('amelia.davis@lincolnuni.ac.nz', 'Amelia', 'Davis', 'Postgraduate Research Student', NULL, '$2y$12$3xwEhLEEPAT2c.gK3gzRduIOqEV5E4ZEkY8XpSCmM0R5sOKSrpy5m', 'student', 'active'),
    ('aria.evans@lincolnuni.ac.nz', 'Aria', 'Evans', 'Bachelor of Commerce Student', NULL, '$2y$12$8sX7HNHy1iS5rfmoRssvceZS5vpoK1GI0XAMndfHcwspiUqT3TQ/G', 'student', 'active'),
    ('benjamin.fisher@lincolnuni.ac.nz', 'Benjamin', 'Fisher', 'Master of Applied Computing Student', NULL, '$2y$12$8wUl/R6eM/rtwnuD8H3KVut7bf21haxxDTY4isXylSXdJGOyTWFky', 'student', 'active'),
    ('charlotte.garcia@lincolnuni.ac.nz', 'Charlotte', 'Garcia', 'Bachelor of Agricultural Science Student', NULL, '$2y$12$/DnSzqQJUIqGulyK6J4g9uaPfQOgoGIGXa3GHDy2qyFFQjenq77D.', 'student', 'active'),
    ('daniel.harris@lincolnuni.ac.nz', 'Daniel', 'Harris', 'Postgraduate Research Student', NULL, '$2y$12$cOl3YRBH1OLZb9VK9GQzfuKt1VrIzPjBmdI3gWHMI5zRWwzUbijH.', 'student', 'active'),
    ('ethan.ito@lincolnuni.ac.nz', 'Ethan', 'Ito', 'Bachelor of Commerce Student', NULL, '$2y$12$a3ARWk1hu4RMRNKw3mFqmeKu0iQFHy/G2AB0j5EX6La4hwKd40QzS', 'student', 'active'),
    ('eva.jones@lincolnuni.ac.nz', 'Eva', 'Jones', 'Master of Applied Computing Student', NULL, '$2y$12$FWTDJ/QxB2.kbcyyIklRve.oepwPZwYgbgaNF3WE7DT2fpxSv.BIC', 'student', 'active'),
    ('fatima.kaur@lincolnuni.ac.nz', 'Fatima', 'Kaur', 'Bachelor of Agricultural Science Student', NULL, '$2y$12$mdAkEDxmLJIywlJY0jZG0em9pME2l2jwk4uLn/X36FsS2zn5jYZtK', 'student', 'active'),
    ('finn.lee@lincolnuni.ac.nz', 'Finn', 'Lee', 'Postgraduate Research Student', NULL, '$2y$12$RjBDCOxtUD711CH./yCyYOC90vO65bBBlwwXrsUqARXtmaU93r3.6', 'student', 'active'),
    ('grace.martin@lincolnuni.ac.nz', 'Grace', 'Martin', 'Bachelor of Commerce Student', NULL, '$2y$12$Y8okZB/z09zavAriOEW79O7FqIvqynMjcbAltw4KaNUQ1n4coqMvW', 'student', 'active'),
    ('hana.ngata@lincolnuni.ac.nz', 'Hana', 'Ngata', 'Master of Applied Computing Student', NULL, '$2y$12$vpYbh5Jq6tRqbYMEltxviu5tJLL.innE1K0DroQL/hf5CG5kOfG.m', 'student', 'active'),
    ('harper.oconnor@lincolnuni.ac.nz', 'Harper', 'O''Connor', 'Bachelor of Agricultural Science Student', NULL, '$2y$12$rBChByRPwCFaqCXK0Dn5CuLXhM0ex3iGQ8C/aH.y4ogl6hgbPiYjO', 'student', 'inactive'),
    ('henry.patel@lincolnuni.ac.nz', 'Henry', 'Patel', 'Postgraduate Research Student', NULL, '$2y$12$cRAXA.aGJqksEdF/yIQ/V.WIbXKYJ/5zl2gkQ4VWLuW.HVhez7anG', 'student', 'active'),
    ('isla.quinn@lincolnuni.ac.nz', 'Isla', 'Quinn', 'Bachelor of Commerce Student', NULL, '$2y$12$wbD4P3E2XMB1tW64Qkdcb.0nBQhUVSggnZ1N0nJcTbV1gcGS9Zzke', 'student', 'active'),
    ('jack.roberts@lincolnuni.ac.nz', 'Jack', 'Roberts', 'Master of Applied Computing Student', NULL, '$2y$12$Enkxb7CMMMlNaZTlv/ISZOhr2MsCebL.3VvtTCmqC605W6JSk5722', 'student', 'active'),
    ('james.singh@lincolnuni.ac.nz', 'James', 'Singh', 'Bachelor of Agricultural Science Student', NULL, '$2y$12$XKSK0jRCMMvwREnmTR/JU.ATG9GsZbHHqJMamM47wF/Z4oPD/xBpK', 'student', 'active'),
    ('jasmine.taylor@lincolnuni.ac.nz', 'Jasmine', 'Taylor', 'Postgraduate Research Student', NULL, '$2y$12$HP.6mB7oAJMo4W8uhWlmi.kzjOzhVfQpYh3KurdultAk41pTkfRn2', 'student', 'active'),
    ('kai.upton@lincolnuni.ac.nz', 'Kai', 'Upton', 'Bachelor of Commerce Student', NULL, '$2y$12$iNiu2rsecY.9haIuDw6.DeLRsNJfIjJDrVQfCLeThR3o0StzbEyvS', 'student', 'active'),
    ('layla.walker@lincolnuni.ac.nz', 'Layla', 'Walker', 'Master of Applied Computing Student', NULL, '$2y$12$Xg4tEximcDHuehBkzRRmZOvi.uY5SNvj1DDfAU5FfZGD5.0QT8VzS', 'student', 'active'),
    ('leo.xu@lincolnuni.ac.nz', 'Leo', 'Xu', 'Bachelor of Agricultural Science Student', NULL, '$2y$12$/rPXDy92CsGHH1DspMKLw.MeVprhOH1DvkwPwasAJYm29nT7lAkpq', 'student', 'active'),
    ('liam.young@lincolnuni.ac.nz', 'Liam', 'Young', 'Postgraduate Research Student', NULL, '$2y$12$Uj6xsmSOKzLmrxp4sAjgy.eF3kcU.hByQth.fG8wA.rgYhZAfIxn6', 'student', 'active'),
    ('lily.zhang@lincolnuni.ac.nz', 'Lily', 'Zhang', 'Bachelor of Commerce Student', NULL, '$2y$12$nnEOWqWiRviXcfCZZTHIJeagvNH/lhUsyAyWiGpXHEJNOPtvfc7DO', 'student', 'active'),
    ('lucas.brown@lincolnuni.ac.nz', 'Lucas', 'Brown', 'Master of Applied Computing Student', NULL, '$2y$12$zFJOQAuAza0xdnPTHsZKxe5mC8jjTCYeRGxoI3puT2UeBUyEzKBDK', 'student', 'active'),
    ('maya.clark@lincolnuni.ac.nz', 'Maya', 'Clark', 'Bachelor of Agricultural Science Student', NULL, '$2y$12$7xIDMGQtiQoHTyyEWaH4BOWEN4xrP1hB9x7oDoq5EuowBdXNyQGVS', 'student', 'active'),
    ('mia.edwards@lincolnuni.ac.nz', 'Mia', 'Edwards', 'Postgraduate Research Student', NULL, '$2y$12$oMZjGXccA7/69NyWGQhf6uxxEplQVHAj1C5HS7biKyeVs96mCxyK2', 'student', 'active'),
    ('noah.fraser@lincolnuni.ac.nz', 'Noah', 'Fraser', 'Bachelor of Commerce Student', NULL, '$2y$12$1iX8pGuNIfnC8AJZBNpdiu1zk0.CSe6EcMQJwCdWqN4fRqxjy2RT.', 'student', 'active'),
    ('nora.green@lincolnuni.ac.nz', 'Nora', 'Green', 'Master of Applied Computing Student', NULL, '$2y$12$6lvyNmlrizv4s.LzB1dr7eOhCTLVfPyeMr5T8.fHoQ7yunrBTIhVS', 'student', 'active'),
    ('oliver.hall@lincolnuni.ac.nz', 'Oliver', 'Hall', 'Bachelor of Agricultural Science Student', NULL, '$2y$12$BJlY6SVVRF6VnSqtM.MQgOrmwIxf0lf5DjTLbVhUsm8ChgpbwNCIy', 'student', 'active'),
    ('olivia.king@lincolnuni.ac.nz', 'Olivia', 'King', 'Postgraduate Research Student', NULL, '$2y$12$E7H3xajhaQtPXx7sp8fv9ei4/TK8OuO.PNafTEmR57Tn91X99SWfq', 'student', 'active'),
    ('oscar.lewis@lincolnuni.ac.nz', 'Oscar', 'Lewis', 'Bachelor of Commerce Student', NULL, '$2y$12$sJUsd/MYlUK4GpRWpj6I7eZR1VQ98SonImoDCMPENR9.j24ckLG4G', 'student', 'active'),
    ('priya.mitchell@lincolnuni.ac.nz', 'Priya', 'Mitchell', 'Master of Applied Computing Student', NULL, '$2y$12$2wMZGCh.H2Q2giyKsrD8T.eDId2Vj7X0K7amC7Zz9MEPCbrzseXyi', 'student', 'active'),
    ('riley.nelson@lincolnuni.ac.nz', 'Riley', 'Nelson', 'Bachelor of Agricultural Science Student', NULL, '$2y$12$K8dyfpYzdQdu9agmrYtSZ.N.Yv4ucgw25mBYLj/ueopzS5OYvrYeK', 'student', 'active'),
    ('ruby.owens@lincolnuni.ac.nz', 'Ruby', 'Owens', 'Postgraduate Research Student', NULL, '$2y$12$lBP3ro631F99Oj8NU5du4uIoAI/kXdPyCOICzgrJ8qicY8A3GfYuq', 'student', 'active'),
    ('samuel.parker@lincolnuni.ac.nz', 'Samuel', 'Parker', 'Bachelor of Commerce Student', NULL, '$2y$12$/5vu2NuM2kz8R5b56DLqdOK.sc4TMaxi5DieLG2KNi0tUSggW1.T2', 'student', 'active'),
    ('sofia.reid@lincolnuni.ac.nz', 'Sofia', 'Reid', 'Master of Applied Computing Student', NULL, '$2y$12$eJAFYzZkHAehDD91zkyQ7OnfrjFrSA2.nWJatJKtJxOdwk4C59xXe', 'student', 'active'),
    ('sophie.scott@lincolnuni.ac.nz', 'Sophie', 'Scott', 'Bachelor of Agricultural Science Student', NULL, '$2y$12$EBqBH2Hui8bfExaMlGY0k.8ayaes78ri6dO6kkSf2dnLcCdJuVJ5K', 'student', 'active'),
    ('tane.turner@lincolnuni.ac.nz', 'Tane', 'Turner', 'Postgraduate Research Student', NULL, '$2y$12$PHuiDrxJRdYuNfo9DCtfrOnQW.PtJ7kPaBShe111eMJZt7lYDrn4W', 'student', 'active'),
    ('theo.wilson@lincolnuni.ac.nz', 'Theo', 'Wilson', 'Bachelor of Commerce Student', NULL, '$2y$12$J2/4sRQmp7Td.3tp0D673u8G7GcgYySdKgYmaeRvv1RBbEyO0CbM2', 'student', 'active'),
    ('thomas.adams@lincolnuni.ac.nz', 'Thomas', 'Adams', 'Master of Applied Computing Student', NULL, '$2y$12$Kh3KWqeFOXmFkzlElbpsau1lYc391Vd/J8vy.YGqjpnQOBS5T0p0G', 'student', 'active'),
    ('victoria.bell@lincolnuni.ac.nz', 'Victoria', 'Bell', 'Bachelor of Agricultural Science Student', NULL, '$2y$12$4zthsPQDduDsy.nrTSCoE.S0iRV9OplUmDf0K.4PXdGdfprD7OhgO', 'student', 'active'),
    ('william.cooper@lincolnuni.ac.nz', 'William', 'Cooper', 'Postgraduate Research Student', NULL, '$2y$12$k9dxsb0C7nHiJ/f33l86qu.frDMdcQvEU8Cqji.ly/X8I65QxZ9nC', 'student', 'active'),
    ('yuki.dunn@lincolnuni.ac.nz', 'Yuki', 'Dunn', 'Bachelor of Commerce Student', NULL, '$2y$12$Zsg8bioL0X8fGbr0Ti7AN.23V5b1WJMneTHU4eI2tnWoddCfVmaKe', 'student', 'active'),
    ('zara.ellis@lincolnuni.ac.nz', 'Zara', 'Ellis', 'Master of Applied Computing Student', NULL, '$2y$12$CdQNpCrBwzNa8kr878a6WuhvnvyGsaWcGq5Gm1Ji0OR5LdbgsrRfW', 'student', 'active'),
    ('zoe.ford@lincolnuni.ac.nz', 'Zoe', 'Ford', 'Bachelor of Agricultural Science Student', NULL, '$2y$12$DXE6cfq729XZvE9/fz.Euu0HSpb.h5/CMZLQVEBBA3ng4eEvygpjm', 'student', 'active'),
    ('anika.gray@lincolnuni.ac.nz', 'Anika', 'Gray', 'Postgraduate Research Student', NULL, '$2y$12$D0QiBYluDusFWMwsEG543ugeqr/0WiB1.79YcXITMN2sn.yhGCfEq', 'student', 'active'),
    ('caleb.hughes@lincolnuni.ac.nz', 'Caleb', 'Hughes', 'Bachelor of Commerce Student', NULL, '$2y$12$3g5CbF2QTPl1UXg4BNG9fOnt4v72CSPmx530cGSJfA16orl4yscGy', 'student', 'active'),
    ('mei.irwin@lincolnuni.ac.nz', 'Mei', 'Irwin', 'Master of Applied Computing Student', NULL, '$2y$12$XyegxIzpqKgggs8oa5ljTuXdzYMGUrGCmP8VNDfQ25QeJ6B89v.6S', 'student', 'active'),
    ('alice.kelly@lincoln.ac.nz', 'Alice', 'Kelly', 'Lecturer in Applied Computing', NULL, '$2y$12$mZ/L6lzlEWaVtOjan59DC.o7LD0P534Rflo8.VaoMKAct8QOLY0IS', 'staff', 'active'),
    ('brian.morgan@lincoln.ac.nz', 'Brian', 'Morgan', 'Research Coordinator', NULL, '$2y$12$W7yD3/HNg/6bBypW06COHOJGrzTs/FXUg6TDPZUYwAv9ra4FFzdLq', 'staff', 'active'),
    ('catherine.nash@lincoln.ac.nz', 'Catherine', 'Nash', 'Programme Administrator', NULL, '$2y$12$unresohF2jk5kSKHc0im5uNZDhIUYED/igVgiRS8LKUmjdenYuHWu', 'staff', 'active'),
    ('david.price@lincoln.ac.nz', 'David', 'Price', 'Senior Tutor', NULL, '$2y$12$Cb1jTF7E614oJ7VctlpgbeZqqp9nsapKa.UDyI9OQULyYvvZu45Wm', 'staff', 'active'),
    ('emma.russell@lincoln.ac.nz', 'Emma', 'Russell', 'Academic Services Adviser', NULL, '$2y$12$O6gCZfJ.7gNGICxwkg97hu810kPjDTojym./qtebCPdxlvUNXufpS', 'staff', 'active'),
    ('george.stewart@lincoln.ac.nz', 'George', 'Stewart', 'Lecturer in Applied Computing', NULL, '$2y$12$9lndqYSaS4CCqZC.XiXEnuv.c.oUJMmC8hi.Hd3gOLO1.kL.lR0hW', 'staff', 'active'),
    ('helen.thompson@lincoln.ac.nz', 'Helen', 'Thompson', 'Research Coordinator', NULL, '$2y$12$85k8GYrZElzcS1/0KIB9zOkt3gaLNmNqTxNRAI59b.nrbmjKEtGbS', 'staff', 'inactive'),
    ('ian.ward@lincoln.ac.nz', 'Ian', 'Ward', 'Programme Administrator', NULL, '$2y$12$wDlz0xrW9yOu0zI.gdNBLuBliGbqICJJ3jPbt0cCDRZkLufi1MXY.', 'staff', 'active'),
    ('julia.white@lincoln.ac.nz', 'Julia', 'White', 'Senior Tutor', NULL, '$2y$12$jehOBCE5to9.qpvnPSp2cOX8khuTL4JnxO2fG5doMolrqL9r1ZRI.', 'staff', 'active'),
    ('kevin.wood@lincoln.ac.nz', 'Kevin', 'Wood', 'Academic Services Adviser', NULL, '$2y$12$..7OvtU0qf2ZT7BOe45hE.xpWEROV76lifA8eUgHoDyOVtK2nkHM.', 'staff', 'active'),
    ('laura.wright@lincoln.ac.nz', 'Laura', 'Wright', 'System Administrator', NULL, '$2y$12$rmEaxhrJj8uqrk3q1Q5i.eo9g/uJNragrTPpZHte7HFPnJ1nn2ZGy', 'admin', 'active'),
    ('michael.murray@lincoln.ac.nz', 'Michael', 'Murray', 'System Administrator', NULL, '$2y$12$2Y0NGo1mmC6LcCMMbdFwI.zgofmooeYyanp8BHYelMx37TqnYavZe', 'admin', 'active');

-- Create 100 realistic projects.
-- The first 40 are owned by staff/admin users so they can be shared.
INSERT INTO projects (owner_id, project_name, description)
SELECT
    CASE
        WHEN project_number <= 40
            THEN 51 + ((project_number - 1) % 12)
        ELSE 1 + ((project_number - 41) % 62)
    END,
    CASE ((project_number - 1) % 10)
        WHEN 0 THEN 'Teaching Preparation ' || project_number
        WHEN 1 THEN 'Research Milestones ' || project_number
        WHEN 2 THEN 'Coursework Planner ' || project_number
        WHEN 3 THEN 'Student Support Actions ' || project_number
        WHEN 4 THEN 'Laboratory Activities ' || project_number
        WHEN 5 THEN 'Professional Development ' || project_number
        WHEN 6 THEN 'Community Engagement ' || project_number
        WHEN 7 THEN 'Assessment Schedule ' || project_number
        WHEN 8 THEN 'Sustainability Initiative ' || project_number
        ELSE 'Semester Priorities ' || project_number
    END,
    CASE ((project_number - 1) % 6)
        WHEN 0 THEN 'Plan and track teaching-related activities for the semester.'
        WHEN 1 THEN 'Coordinate research tasks, reviews, and key deliverables.'
        WHEN 2 THEN 'Organise coursework, deadlines, and study priorities.'
        WHEN 3 THEN 'Record follow-up actions for student and staff support.'
        WHEN 4 THEN 'Prepare resources, bookings, and safety checks.'
        ELSE 'Track important university work and completion progress.'
    END
FROM generate_series(1, 100) AS project_number;

-- Create exactly 500 tasks: five for each project.
INSERT INTO tasks (
    project_id,
    task_name,
    description,
    priority,
    due_date,
    is_complete
)
SELECT
    project_id,
    CASE task_number
        WHEN 1 THEN 'Review project requirements'
        WHEN 2 THEN 'Prepare supporting resources'
        WHEN 3 THEN 'Complete the main activity'
        WHEN 4 THEN 'Check progress with stakeholders'
        ELSE 'Final review and close-out'
    END,
    CASE task_number
        WHEN 1 THEN 'Read the project information and confirm the expected outcomes.'
        WHEN 2 THEN 'Gather the files, references, and resources needed for the work.'
        WHEN 3 THEN 'Carry out the central piece of work for this project.'
        WHEN 4 THEN 'Confirm progress, resolve issues, and record follow-up actions.'
        ELSE 'Check quality, update completion status, and document the result.'
    END,
    CASE ((project_id + task_number) % 3)
        WHEN 0 THEN 'low'::task_priority
        WHEN 1 THEN 'medium'::task_priority
        ELSE 'high'::task_priority
    END,
    CASE ((project_id + task_number) % 5)
        WHEN 0 THEN NULL
        WHEN 1 THEN CURRENT_DATE - ((project_id % 20) + 1)
        WHEN 2 THEN CURRENT_DATE + ((project_id % 30) + 1)
        WHEN 3 THEN CURRENT_DATE - ((project_id % 10) + 1)
        ELSE CURRENT_DATE + ((project_id % 45) + 1)
    END,
    ((project_id + task_number) % 4 = 0)
FROM projects
CROSS JOIN generate_series(1, 5) AS task_number;

-- Give every user membership in at least one shared staff/admin project.
INSERT INTO project_members (project_id, user_id)
SELECT
    1 + ((user_id + 1) % 12),
    user_id
FROM users;

-- Add 38 additional unique memberships, producing exactly 100 total.
INSERT INTO project_members (project_id, user_id)
SELECT
    13 + ((user_id + 4) % 12),
    user_id
FROM users
WHERE user_id <= 38;

COMMIT;

-- Verification output.
SELECT user_role, COUNT(*) AS user_count
FROM users
GROUP BY user_role
ORDER BY user_role;

SELECT COUNT(*) AS project_count FROM projects;
SELECT COUNT(*) AS task_count FROM tasks;
SELECT COUNT(*) AS project_member_count FROM project_members;

SELECT COUNT(*) AS users_without_shared_project
FROM users u
WHERE NOT EXISTS (
    SELECT 1
    FROM project_members pm
    WHERE pm.user_id = u.user_id
);