list1 = ['.xls', '.xlsx', '.doc', '.docx', '.pdf', '.zip', '.sql', '.bak', '.csv', '.txt', '.jpg', '.psd', '.mp4', '.png', '.dll', '.exe', '.tif', '.avi', '.pst', '.log']
envlist2 = ['.pdf', '.xls', '.xlsx', '.doc', '.docx', '.ppt', '.pptx', '.txt', '.rtf', '.csv', '.tsv', '.pst', '.sql', '.db', '.dbf', '.mdb', '.bak', '.zip', '.gz', '.tar', '.rar', '.7z', '.jpg', '.png', '.gif', '.mp3', '.mp4', '.xml', '.html', '.htm', '.log', '.odt', '.ods', '.odp', '.odg', '.odf', '.od', '.exe', '.dll', '.avi', '.bat', '.reg', '.css', '.js', '.lnk', '.sys', '.ini', '.wav', '.bmp', '.tif', '.iso', '.dat', '.psd', '.ai', '.eps']

# Convert lists to sets
set1 = set(list1)
set2 = set(envlist2)

# Find missing values from list1 when compared to list2
missing_values = set1.difference(set2)
missing_values1 = set2.difference(set1)

print("Missing values from list1 when compared to list2:")
print(missing_values)
print(missing_values1)
