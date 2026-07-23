-- libraryManagementSystemDataPrepare-- GenerationTimeBetween: 2023-01-01 12:00:00

-- UserTableData
INSERT INTO user (StudentId, Name, Password, IsAdmin, tel) VALUES
('admin', 'SystemManagement', 'e10adc3949ba59abbe56e057f20f883e', 1, 'admin@library.com'),
('TEST001', 'Test User', 'e10adc3949ba59abbe56e057f20f883e', 0, 'test@email.com');

-- bookTableData
INSERT INTO book (BookId, BookName, Auth, Category, Publisher, PublishTime, NumStorage, NumCanBorrow, NumBookinged) VALUES
('ISBN001', 'PythonCodeProcessInput', 'Sam', 'DesignCalculateMachine', 'PersonOutputEdition', '2023-01-01', 10, 8, 0);

-- borrowTableData
INSERT INTO user_book (StudentId, BookId, BorrowTime, ReturnTime, BorrowState, BookingState) VALUES
('TEST001', 'ISBN001', '2023-01-01', NULL, 1, 0);
