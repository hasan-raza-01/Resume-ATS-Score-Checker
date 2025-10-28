import httpx, asyncio

url = "http://localhost:8080/upload"

# For async support
async def upload_files():
    async with httpx.AsyncClient(timeout=None) as client:
        with open('/home/hasan/Artificial-Intelligence/projects/Resume-ATS-Score-Checker/resumes/1.docx', 'rb') as f1, \
        open('/home/hasan/Artificial-Intelligence/projects/Resume-ATS-Score-Checker/resumes/1.pdf', 'rb') as f2, \
        open('/home/hasan/Artificial-Intelligence/projects/Resume-ATS-Score-Checker/resumes/1.html', 'rb') as f3, \
        open('/home/hasan/Artificial-Intelligence/projects/Resume-ATS-Score-Checker/resumes/2.docx', 'rb') as f4, \
        open('/home/hasan/Artificial-Intelligence/projects/Resume-ATS-Score-Checker/resumes/2.pdf', 'rb') as f5, \
        open('/home/hasan/Artificial-Intelligence/projects/Resume-ATS-Score-Checker/resumes/2.html', 'rb') as f6, \
        open('/home/hasan/Artificial-Intelligence/projects/Resume-ATS-Score-Checker/resumes/3.docx', 'rb') as f7, \
        open('/home/hasan/Artificial-Intelligence/projects/Resume-ATS-Score-Checker/resumes/3.pdf', 'rb') as f8, \
        open('/home/hasan/Artificial-Intelligence/projects/Resume-ATS-Score-Checker/resumes/3.html', 'rb') as f9, \
        open('/home/hasan/Artificial-Intelligence/projects/Resume-ATS-Score-Checker/resumes/3_images.docx', 'rb') as f10, \
        open('/home/hasan/Artificial-Intelligence/projects/Resume-ATS-Score-Checker/resumes/3_images.pdf', 'rb') as f11, \
        open('/home/hasan/Artificial-Intelligence/projects/Resume-ATS-Score-Checker/resumes/3_js_heavy.html', 'rb') as f12:
            files = [
                ('files', f1),
                ('files', f2),
                ('files', f3),
                ('files', f4),
                ('files', f5),
                ('files', f6),
                ('files', f7),
                ('files', f8),
                ('files', f9),
                ('files', f10),
                ('files', f11),
                ('files', f12),

            ]
            
            response = await client.post(url, files=files)
            print(response.json())

asyncio.run(upload_files())
print("\n------------------------------------------------------------------------------------------------------------\n")
